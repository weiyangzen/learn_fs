# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-pip.h

## Purpose
`cvmx-pip.h` is the hand-written interface layer for Octeon Packet Input Processing. It turns the generated PIP CSR definitions into small inline configuration and statistics helpers, defines packet parser error codes, and documents the custom packet input header that external hardware can prepend before PIP parses a packet.

## Important APIs, Types, And Functions
Constants define `CVMX_PIP_NUM_INPUT_PORTS` as 48 and `CVMX_PIP_NUM_WATCHERS` as 4. Error enums define L4 errors (`cvmx_pip_l4_err_t`), IP exceptions (`cvmx_pip_ip_exc_t`), and receive errors (`cvmx_pip_rcv_err_t`), unified by `cvmx_pip_err_t`. `cvmx_pip_port_status_t` aggregates drop, octet, packet, raw PCI, multicast/broadcast, length-bin, FCS/runt/oversize, inbound packet/octet, and inbound error counters. `cvmx_pip_pkt_inst_hdr_t` models the 64-bit external instruction header containing rawfull, parse mode, skip length, QoS, group, RS flag, tag type, and tag.

Inline helpers are `cvmx_pip_config_port()`, `cvmx_pip_config_vlan_qos()`, `cvmx_pip_config_diffserv_qos()`, `cvmx_pip_get_port_status()`, `cvmx_pip_config_crc()`, `cvmx_pip_tag_mask_clear()`, and `cvmx_pip_tag_mask_set()`. A deprecated watcher helper is present under `#if 0`, documenting why direct CSR access is preferred for pass 2 hardware.

## Control Flow
The helpers are direct CSR sequences. `cvmx_pip_config_port()` writes per-port config and tag config. VLAN and DiffServ helpers zero a CSR union, set the QoS field, and write it. `cvmx_pip_get_port_status()` writes `CVMX_PIP_STAT_CTL` to select clear-on-read behavior, reads the stat register family and inbound counters, fills the aggregate status struct, then applies a pass-1 errata workaround that derives drop counts from inbound minus processed counters. `cvmx_pip_config_crc()` programs CRC only on CN38XX/CN58XX. Tag-mask helpers clear 16 CSR entries per mask or read-modify-write byte-selection bits.

## State And Persistence
State changes are hardware-resident PIP configuration and counters. The only memory state is caller-provided `cvmx_pip_port_status_t`. `clear` in `cvmx_pip_get_port_status()` can consume statistics globally for the target reads. Tag-mask programming persists until changed or reset and affects future work queue tag generation.

## Dependencies And Integration Points
The file includes `cvmx-wqe.h`, `cvmx-fpa.h`, and `cvmx-pip-defs.h`. It depends on CSR accessors, `OCTEON_IS_MODEL()`, `cvmx_octeon_is_pass1()`, and packet-buffer/work-queue definitions. It integrates with IPD receive initialization, POW scheduling, network drivers that interpret PIP error codes in WQEs, and statistics reporting.

## Risks
The helpers trust caller-supplied port, VLAN, DiffServ, mask, and offset values; indexed CSR macros mask out-of-range values. The pass-1 drop-counter workaround can underflow if assumptions about CRC bytes or counter ordering change. `cvmx_pip_tag_mask_set()` computes `mask_index * 16 + offset / 8` without validating the 64-entry hardware table, so large offsets can wrap in the CSR macro. Statistics reads are not atomic with packet arrival, and clear-on-read can surprise concurrent readers. CRC configuration silently does nothing on unsupported models.

## Test Signals
Tests should verify CSR writes for port config, VLAN and DiffServ QoS mappings, CRC programming on supported and unsupported models, status aggregation from mocked CSR values, pass-1 drop-counter correction, tag-mask clear and bit-setting across byte boundaries, and packet receive integration where WQE error code, group, QoS, and tag match configured policy.
