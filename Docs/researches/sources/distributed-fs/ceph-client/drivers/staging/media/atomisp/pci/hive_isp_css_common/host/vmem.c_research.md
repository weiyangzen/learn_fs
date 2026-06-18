# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/hive_isp_css_common/host/vmem.c

## Purpose

`vmem.c` loads and stores ISP VMEM/BAMEM vectors, including bit packing/unpacking between host words and ISP vector element widths..

## Important APIs, Types, And Data

Key includes: `isp.h`, `vmem.h`, `vmem_local.h`, `ia_css_device_access.h`, `assert_support.h`. Important macros/constants include `uedge_bits`, `move_lower_bits`, `move_upper_bits`, `move_word`. Important types include `unsigned`, `hive_uedge`. Important functions include `move_subword()`, `hive_sim_wide_unpack()`, `hive_sim_wide_pack()`, `load_vector()`, `store_vector()`, `isp_vmem_load()`, `isp_vmem_store()`, `isp_vmem_2d_load()`, `isp_vmem_2d_store()`.

## Control Flow

The low-level helpers move arbitrary bit ranges between 64-bit host words so vectors can be packed or unpacked according to `ISP_VEC_ELEMBITS`. Public load/store APIs assert vector alignment and widths, step through 1D or 2D VMEM rows in `ISP_NWAY` chunks, and use either `ia_css_device_load/store()` or HRT master-port access depending on `HRT_MEMORY_ACCESS`.

## State And Persistence Behavior

The persistent state is hardware or firmware-visible state, not normal kernel heap state. Register writes persist in the ISP CSS device until overwritten or reset; shared structs and memory windows persist in SP/ISP DMEM, VMEM/BAMEM, HMEM, DDR, input-buffer SRAM, or GP-device registers depending on the subsystem.

## Dependencies And Integration Points

Dependencies are local to the AtomISP CSS host stack: `type_support.h` scalar types, `system_global.h`/`system_local.h` base addresses and IDs, block-specific public/private headers, `assert_support.h`, `device_access.h` or `ia_css_device_access.h`, and low-level HRT register/memory operations. Integration points are the higher-level CSS pipeline code that configures sensors, DMA, GDC, input formatting, IRQ delivery, SP/ISP execution, and diagnostics through these wrappers.

## Risks And Edge Cases

- Most validation relies on `assert()`/`OP___assert()`, so production builds with assertions disabled may convert bad IDs, sizes, or enum values into invalid hardware accesses.
- The code is tightly coupled to RTL register indexes, bit positions, and shared firmware layouts; a one-bit drift can silently program the wrong CSS block.
- Many helpers are thin wrappers around MMIO or firmware memory and do not serialize concurrent callers, so sequencing must be enforced by the higher-level CSS pipeline.
- The bit-moving helpers use shifts near word width boundaries; malformed element widths or non-vector-aligned pointers can corrupt adjacent vector data.

## Test Signals

- Build AtomISP with the relevant CSS blocks enabled and with both inline and out-of-line helper configurations where supported.
- Run static checks that compare register indexes, bit widths, enum ranges, and shared struct sizes against the generated hardware definitions.
- Exercise representative sensor/input-system startup, DMA transfers, GDC LUT programming, IRQ delivery/clear, FIFO monitor snapshots, SP/ISP start/idle, and debug-buffer reads on hardware or the HSS/simulation model.
