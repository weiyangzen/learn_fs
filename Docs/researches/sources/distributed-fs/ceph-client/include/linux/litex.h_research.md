<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/litex.h -->
# sources/distributed-fs/ceph-client/include/linux/litex.h

## Purpose
This header provides LiteX CSR access helpers. LiteX exposes many registers as arrays of 8-bit subregisters, so these helpers assemble and split 8, 16, 32, and 64-bit values over byte-wide MMIO locations.

## Important APIs, Types, and Functions
Internal helpers `_write_litex_subregister()` and `_read_litex_subregister()` operate on one byte-wide register slot using `writeb`/`readb`. Public helpers `litex_write8`, `litex_write16`, `litex_write32`, `litex_write64`, `litex_read8`, `litex_read16`, `litex_read32`, and `litex_read64` provide typed CSR access.

## Control Flow
Write helpers decompose the value into big-endian byte lanes and write successive subregisters. Read helpers read successive subregisters and reconstruct the value by shifting and ORing.

## State and Persistence Behavior
State is external hardware register state. The helpers do not cache values or persist data; ordering and visibility follow MMIO access semantics from `linux/io.h`.

## Dependencies and Integration Points
It depends on `linux/io.h` and integrates with LiteX platform drivers for FPGA-generated SoCs, soft peripherals, and SoC controller blocks.

## Risks and Test Signals
Risks include using the helpers on non-LiteX register layouts, wrong register width, endianness mismatch, and missing barriers around higher-level protocols. Test signals are CSR readback tests, hardware smoke tests, and bus fault or timeout diagnostics from LiteX peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/litex.h -->
