# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-util.h

## Purpose
`cvmx-helper-util.h` contains small common utilities for Octeon packet helpers. It declares mode-to-string, RED setup, version, GMX setup, IPD port mapping, and interface reverse-mapping functions, and it implements inline helpers for first/last IPD port lookup and freeing packet data attached to a work queue entry.

## Important APIs, Types, And Functions
Key APIs are `cvmx_helper_interface_mode_to_string`, `cvmx_helper_setup_red`, `cvmx_helper_get_version`, `__cvmx_helper_setup_gmx`, `cvmx_helper_get_ipd_port`, `cvmx_helper_get_first_ipd_port`, `cvmx_helper_get_last_ipd_port`, `cvmx_helper_free_packet_data`, `cvmx_helper_get_interface_num`, and `cvmx_helper_get_interface_index_num`.

## Control Flow
`cvmx_helper_get_first_ipd_port()` delegates to `cvmx_helper_get_ipd_port(interface, 0)`. `cvmx_helper_get_last_ipd_port()` adds the interface port count minus one. `cvmx_helper_free_packet_data()` reads the WQE buffer count, handles the special `NO_WPTR` case where the first packet buffer is also the WQE and must not be freed, then walks the linked buffer chain by reading the next pointer from `buffer_ptr.s.addr - 8` before returning each buffer to FPA.

## State And Persistence
Most APIs return derived configuration or program hardware elsewhere. The inline packet-free function mutates persistent FPA pool state by returning buffers and does not free the WQE itself. It relies on packet buffer back-pointers and next-buffer metadata stored in packet memory.

## Dependencies And Integration Points
It depends on `struct cvmx_wqe`, `union cvmx_buf_ptr`, `cvmx_ptr_to_phys`, `cvmx_phys_to_ptr`, and `cvmx_fpa_free`, plus common helper APIs. It is used by packet receive paths and helper initialization code for IPD/PKO/GMX setup and RED configuration.

## Risks
Incorrect buffer metadata can cause freeing the wrong physical address or pool. The `NO_WPTR` detection compares the WQE physical address to the packet buffer start and must stay aligned with IPD configuration. `cvmx_helper_get_last_ipd_port()` assumes the interface is initialized and has a positive port count.

## Test Signals
Packet lifecycle tests should verify all buffers are returned for single- and multi-buffer packets, the WQE is preserved in `NO_WPTR` mode, FPA pool counts recover after receive/free loops, and first/last IPD port calculations match interface probe results.
