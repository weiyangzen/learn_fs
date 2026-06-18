# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_prbs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_prbs.h` is the deprecated PRBS test input configuration contract in the Intel AtomISP CSS driver. It defines PRBS ids and `struct ia_css_prbs_config` with blanking and two seed values for pseudo-random input generation.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_prbs_config`. Visible enums: `enum ia_css_prbs_id`, `enum ia_css_prbs_id	id;`. Important macros/constants: `__IA_CSS_PRBS_H`, `N_CSS_PRBS_IDS`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Streams select `IA_CSS_INPUT_MODE_PRBS` and place this config in the stream source union; lower input-system code programs the generator.

## State and Persistence Behavior

State is test-generator hardware state seeded from this struct.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are stale deprecated API use and seed/blanking combinations that do not match expected frame dimensions.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 45 lines, 1129 bytes.
