# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc_v1_0_ih_clientid.h

## Purpose

This header defines SOC v1.0 interrupt handler client IDs for AMD GPU interrupt source decoding. It maps hardware client-id numbers from interrupt ring entries to symbolic names and declares `soc_v1_0_ih_clientid_name[]`, a string table expected to be defined elsewhere for logging and diagnostics.

## Important APIs, Types, and Constants

- `extern const char *soc_v1_0_ih_clientid_name[]`: name lookup table for client IDs. The table definition must be sized and indexed consistently with this enum.
- `enum soc_v1_0_ih_clientid`: sparse hardware client IDs:
  - `SOC_V1_0_IH_CLIENTID_IH = 0x00`
  - `ATHUB = 0x02`, `BIF = 0x03`, `RLC = 0x07`, `GFX = 0x0a`, `IMU = 0x0b`
  - media/thermal/memory clients including `VCN1 = 0x0e`, `THM = 0x0f`, `VCN = 0x10`, `VMC = 0x12`
  - command/GC/fabric/power clients including `GRBM_CP = 0x14`, `GC_AID = 0x15`, `ROM_SMUIO = 0x16`, `DF = 0x17`, `PWR = 0x19`, `LSDMA = 0x1a`, `GC_UTCL2 = 0x1b`, `nHT = 0x1c`, `MP0 = 0x1e`, `MP1 = 0x1f`
  - `SOC_V1_0_IH_CLIENTID_MAX` follows the largest assigned ID and will evaluate to `0x20`.
- The include guard is `__SOC_V1_0_IH_CLIENTID_H__`.

## Control Flow

There is no executable control flow in the header. Runtime control flow occurs in consumers: interrupt decoding reads a client-id field from an interrupt vector, compares or switches on the enum value, and may use `soc_v1_0_ih_clientid_name[client_id]` for traces or error messages.

## State and Persistence Behavior

The header has no mutable state. The external name array is read-only string data owned by another translation unit. Interrupt client IDs are transient hardware event metadata, although logs, traces, and error reports can persist decoded names or raw IDs.

## Dependencies and Integration Points

The file has no explicit includes. It integrates with the AMDGPU interrupt handler path, SOC v1.0 interrupt vector parsing, trace/debug printing, and any code that dispatches behavior based on interrupt client. The sparse enum values imply table consumers must tolerate holes in the ID space or provide placeholder names for unassigned IDs.

## Risks

- Array indexing is the main risk. Because IDs are sparse, `soc_v1_0_ih_clientid_name[]` must have entries up to at least `SOC_V1_0_IH_CLIENTID_MAX - 1`, including placeholders for gaps.
- `SOC_V1_0_IH_CLIENTID_MAX` is not a count of explicitly listed clients; it is one past the highest numeric ID. Code that iterates all enum names must account for gaps.
- The `0X1c` spelling for `SOC_V1_0_IH_CLIENTID_nHT` is valid C but visually inconsistent; mechanical parsers expecting lowercase `0x` could trip.
- Incorrect client ID mapping can route interrupts to the wrong handler or make diagnostics misleading.

## Test Signals

- Compile/link checks should catch a missing definition of `soc_v1_0_ih_clientid_name[]` only when a referencing object is linked.
- Unit or debug tests can verify that the name table has a non-null entry for each defined enum constant and safe placeholders for gaps.
- Hardware interrupt tests should confirm that IH, GFX, VCN, VMC, MP0/MP1, and power events decode to expected clients.
- Trace logs from interrupt storms or GPU reset paths can expose out-of-range or unnamed client IDs.
