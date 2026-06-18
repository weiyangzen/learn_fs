# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 46462-48915

## Purpose

This chunk is an auto-generated register shift/mask slice for AMD NBIO 7.0 PCI configuration-space fields. It covers the tail of the `BIF_CFG_DEV0_EPF7_1` endpoint/function block, all of the `BIF_CFG_DEV1_EPF0_1` block, and the beginning of `BIF_CFG_DEV1_EPF1_1` through the MSI-X table register. The macros describe bit positions and masks only; they do not execute hardware access themselves.

The definitions are part of the AMDGPU register contract included by `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. Driver code can combine these names with the corresponding address/default headers to read, compose, or decode NBIO PCIe configuration registers without embedding numeric bit constants.

## Public Surface In This Chunk

The public API is a dense set of C preprocessor macros named:

- `BIF_CFG_DEV0_EPF7_1_*__FIELD__SHIFT` and `BIF_CFG_DEV0_EPF7_1_*__FIELD_MASK` for power-management, PCIe capability, interrupt, SATA, vendor-specific, AER, BAR, power-budget, DPA, ACS, and ARI fields.
- `BIF_CFG_DEV1_EPF0_1_*__FIELD__SHIFT` and `BIF_CFG_DEV1_EPF0_1_*__FIELD_MASK` for a full endpoint/function config block, including standard PCI header fields, PCIe capability structures, MSI/MSI-X, SATA IDP, VC resources, AER, secondary PCIe capability lane equalization controls, ACS, LTR, and ARI.
- `BIF_CFG_DEV1_EPF1_1_*__FIELD__SHIFT` and `BIF_CFG_DEV1_EPF1_1_*__FIELD_MASK` for the start of the next endpoint/function block, from vendor/device IDs through MSI-X table fields.

Each register comment, such as `//BIF_CFG_DEV1_EPF0_1_DEVICE_CNTL`, is followed by one or more shift macros and matching mask macros. Single-bit fields use a one-bit mask at the shifted position; multi-bit fields use contiguous masks sized to the PCIe-defined field width. Masks use `L` suffixes because the generated headers are intended for C preprocessor use in 32-bit register expressions.

## Important Register Families

The standard PCI header fields expose vendor/device IDs, command and status control, revision and class-code bytes, cache-line and latency timer bytes, header/BIST fields, six BAR registers, adapter/subsystem IDs, ROM base, capability pointer, interrupt line/pin, and legacy min/max latency fields. The command/status masks include IO, memory, bus-master, special-cycle, memory-write-invalidate, VGA palette snoop, parity, SERR, fast-back-to-back, interrupt-disable, and status bits such as capabilities-list, master data parity, signaled target abort, received target abort, received master abort, signaled system error, detected parity error, and devsel timing.

The PCI power-management group defines capability-list linkage, PM version/support bits, D1/D2 and PME support, current power state, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PM data. For NBIO 7.0 this chunk also includes `SBRN`, `FLADJ`, and `DBESL_DBESLD` fields adjacent to the PM/USB-style capability area.

The PCIe capability group defines PCIe capability list headers, device capabilities/control/status, link capabilities/control/status, and the PCIe 2.0 capability/control/status set. Fields cover payload sizes, read request size, error-reporting enables, relaxed ordering, no-snoop, FLR, completion timeout, ARI forwarding, AtomicOp support, IDO, LTR, OBFF, target link speed, compliance controls, deemphasis, equalization status, negotiated width/speed, data-link active, and link bandwidth status/interrupt enables.

Interrupt capability fields include MSI and MSI-X. MSI macros describe enable, multiple-message capability/enable, 64-bit address support, per-vector masking, low/high message address, data, mask, and pending bits. MSI-X macros describe capability-list linkage, table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

The chunk also defines extended capability families. AER fields cover uncorrectable status/mask/severity bits for DLP, surprise-down, poison, flow-control, completion-timeout, completion-abort, unexpected-completion, receiver-overflow, malformed TLP, ECRC, unsupported-request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, and TLP prefix blocked conditions; correctable status/mask bits cover receiver, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, correctable internal, and header-log overflow. AER capability/control and header/TLP prefix log registers are exposed as full-width fields.

Other PCIe extended groups in the span include vendor-specific capability headers and scratch registers, BAR enhanced capability per BAR1-BAR6, power-budget data select/data/capability, dynamic power allocation capability/status/control and eight substate allocation registers, ACS capability/control, ARI capability/control, LTR max snoop/no-snoop latency fields, virtual-channel port/resource control and status for `DEV1_EPF0`, and secondary PCIe lane equalization control for lanes 0-15.

## Control Flow And State

There is no runtime control flow in this chunk. The effective control flow is compile-time macro substitution:

1. Driver code includes `nbio_7_0_sh_mask.h`.
2. A caller reads a 32-bit NBIO/PCI config register using an address macro from the companion offset header.
3. The caller isolates a field with `value & *_MASK`, then shifts by `*_SHIFT`, or composes a field value by shifting and masking before writing.

The header does not store state. Persistent state lives in the device's NBIO PCI configuration registers, not in the source tree. Some fields represent write-sensitive hardware state, including error status, interrupt enables/masks, FLR initiation, link retraining, target link speed, power-management controls, BAR control, DPA controls, ACS controls, ARI forwarding, and VC resource controls.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header scheme: address macros are in sibling NBIO offset headers, reset values are in `nbio_7_0_default.h`, and these `_sh_mask` macros provide field extraction/composition constants. It also depends on PCI/PCIe architectural semantics for capability list layout, AER, MSI/MSI-X, ACS, ARI, LTR, VC, DPA, and secondary PCIe extended capability encodings.

Integration points are AMDGPU NBIO and SOC initialization paths that include this header, plus PowerPlay/SMU code that needs the same register constants. The actual hardware access path is outside this header and normally goes through AMDGPU register access helpers and PCI config access helpers. Because the macros are globally named and not scoped by a C type, they are shared constants rather than an encapsulated API.

## Risks And Maintenance Notes

- These definitions must stay synchronized with NBIO 7.0 hardware documentation and the matching address/default headers. A correct mask paired with the wrong address macro would silently decode or program the wrong field.
- The chunk is highly repetitive across endpoint/function blocks. Copy-generation drift is a real risk, especially where `DEV0_EPF7`, `DEV1_EPF0`, and `DEV1_EPF1` differ in which extended capabilities are present.
- Some PCIe status fields are write-one-to-clear or otherwise side-effectful at the hardware level. The masks make those fields easy to target, but callers must still follow hardware clearing and ordering rules.
- Link, power, DPA, VC, ACS, ARI, MSI/MSI-X, and AER control fields affect interrupt routing, isolation, error reporting, power state, and PCIe training. Incorrect use can produce device hangs, lost interrupts, bad isolation, or masked fatal errors.
- The macros use fixed 32-bit-style masks with `L` suffixes. Consumers should avoid sign extension or truncation surprises when mixing them with wider arithmetic and should use the established AMDGPU register helper types.
- The source chunk starts in the middle of the `DEV0_EPF7` block and ends in the middle of the `DEV1_EPF1` block, so complete per-function coverage requires adjacent chunks during merge.

## Test Signals

Useful validation signals include:

- Header compile coverage for translation units that include `nbio_7_0_sh_mask.h`, especially `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `smu10_inc.h`.
- Static checks that every `*_SHIFT` in this chunk has a matching `*_MASK`, and that masks are contiguous and aligned with their shift.
- Cross-header checks that registers named here have matching address entries in the NBIO 7.0 offset header and default entries in `nbio_7_0_default.h` where applicable.
- Runtime PCIe capability validation on NBIO 7.0 hardware: decoded link speed/width, payload size, MSI/MSI-X capability state, AER masks/status, ACS/ARI/LTR capability bits, and DPA/VC fields should match lspci/config-space expectations.
- Error-path tests that inject or observe AER status bits and verify the AMDGPU error handling path decodes, masks, and clears the intended fields without disturbing unrelated bits.
- Power-management and link-training tests around D-state changes, PME status, FLR, target link speed, retrain link, equalization status, and DPA substate controls.
