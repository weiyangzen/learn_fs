# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_pci_id_tbl.h

## Purpose

`t4_pci_id_tbl.h` is an include-time PCI device ID table generator for Chelsio T4, T5, and T6 adapters. It keeps the adapter product ID list in one header while letting different users define macros that expand each entry into the desired table type, function number, and table wrapper.

## Important APIs, Types, and Constants

- Required includer macros:
  - `CH_PCI_DEVICE_ID_TABLE_DEFINE_BEGIN` starts the generated table.
  - `CH_PCI_DEVICE_ID_FUNCTION` selects the PCI function nibble inserted into each ID.
  - `CH_PCI_ID_TABLE_ENTRY(DeviceID)` emits one table entry.
  - `CH_PCI_DEVICE_ID_TABLE_DEFINE_END` finishes the table and supplies the semicolon.
- Optional `CH_PCI_DEVICE_ID_FUNCTION2` makes every product ID emit two entries, one for each function value.
- `CH_PCI_ID_TABLE_FENTRY(devid)` combines the base product ID with the selected function nibble using `((CH_PCI_DEVICE_ID_FUNCTION) << 8)`.
- The header enumerates many T4 IDs (`0x4000` series), T5 IDs (`0x5000` and custom `0x5080`+ series), and T6 IDs (`0x6001` etc. and custom `0x6080`+ series).
- The device ID scheme is documented as `0xVFPP`: ASIC generation in `V`, function in `F`, and product designation in `PP`.

## Control Flow and State Behavior

The file has no runtime control flow. It uses preprocessor control flow to reject missing required macros, define the per-function expansion macro differently depending on whether `CH_PCI_DEVICE_ID_FUNCTION2` is present, and emit the table in manifest order. It owns no state and performs no persistence; its output becomes static driver data in the translation unit that includes it.

## Dependencies and Integration Points

- Intended to be included by PCI driver code that defines Linux PCI ID table wrappers around it, likely using `PCI_DEVICE()`-style entries and `MODULE_DEVICE_TABLE()`.
- Integrates with probe binding: IDs emitted here determine which Chelsio adapters bind to a given driver or function role.
- Shares generation/product naming with the rest of the `cxgb4` adapter initialization logic, which later maps detected device IDs to chip version and port capabilities.
- The include contract deliberately avoids direct Linux PCI header dependency by requiring the includer to supply the table-entry macro.

## Risks and Edge Cases

- Because the header requires caller-provided macros, a malformed includer can generate syntactically valid but semantically wrong tables.
- Missing a product ID prevents automatic driver binding for that adapter; adding an incorrect ID can bind unsupported hardware.
- `CH_PCI_DEVICE_ID_FUNCTION` and optional function 2 must match the driver role: PF0-3, PF4, VF, or other function spaces. Wrong values generate IDs for the wrong PCI function class.
- The file uses a trailing comma strategy inside `CH_PCI_ID_TABLE_FENTRY()` and relies on `CH_PCI_DEVICE_ID_TABLE_DEFINE_END` to close with a semicolon; unusual table macros must tolerate that style.
- T6 entries are less richly commented than T4/T5, so product mapping may require cross-checking with vendor release notes or adjacent driver tables before edits.

## Test Signals

- Build tests catch missing macro definitions, bad table syntax, and duplicate macro expansion issues.
- `modinfo`/module alias output can confirm expected PCI aliases for generated IDs.
- Probe tests on representative T4/T5/T6 PFs and VFs confirm function-nibble correctness.
- PCI ID diff review is important whenever hardware support is added, because runtime tests only cover physically present adapters.
