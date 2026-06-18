# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/bch-regs.h

## Purpose
Defines BCH ECC engine register offsets and bitfield helpers used by the GPMI NAND driver. These macros encode interrupt control, BCH layout selection, flash layout geometry, page size, ECC strength, Galois-field selection, and data chunk sizes for i.MX23/i.MX28 and newer i.MX6-class variants.

## Important APIs, Types, And Functions
The public surface is macro-only: `HW_BCH_CTRL`, `HW_BCH_STATUS0`, `HW_BCH_LAYOUTSELECT`, `HW_BCH_FLASH0LAYOUT0`, `HW_BCH_FLASH0LAYOUT1`, `HW_BCH_VERSION`, IRQ bits, and `BF_BCH_FLASH0LAYOUT*()` field builders. Several helpers consult `GPMI_IS_MX6(x)` to select wider MX6 bit encodings for ECC strength and data-size fields and to enable GF14 selection.

## Control Flow
There is no executable flow. `gpmi-nand.c` computes a `struct bch_geometry`, converts it to `bch_flashlayout0` and `bch_flashlayout1` with these macros, writes the values before BCH DMA operations, and enables/clears BCH completion interrupts through the defined control bits.

## State And Persistence
The header itself stores no state. It describes volatile hardware register state that determines how the BCH block interprets NAND page payload, metadata, ECC chunks, and completion interrupts. Incorrect values affect on-flash ECC layout compatibility.

## Dependencies And Integration Points
Depends on `gpmi-nand.h` type predicates being visible when field-builder macros are used. It is tightly integrated with `gpmi_bch_layout_std()`, `bch_set_geometry()`, `gpmi_nfc_exec_op()`, and the BCH IRQ path.

## Risks
Bitfield helpers have SoC-conditional encodings; using the wrong devdata predicate would program incompatible ECC layout registers. MX6 data-size macros shift values differently than MXS variants. Any change here can break compatibility with existing NAND contents because BCH layout is part of the physical page encoding.

## Test Signals
Unit-level validation can compare generated layout register values for known geometries and SoC types. Hardware signals include successful BCH IRQ completion, correct ECC correction counts, readable pages after reboot, and compatibility with boot ROM expectations.
