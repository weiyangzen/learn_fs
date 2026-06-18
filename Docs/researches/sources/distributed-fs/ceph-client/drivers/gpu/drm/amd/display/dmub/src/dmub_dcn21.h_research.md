# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.h

## Purpose

`dmub_dcn21.h` is the public declaration header for the DCN21 DMUB register table. It inherits the DCN20 common register/function model and exports the DCN21 table symbol.

## Important APIs, Types, And Functions

The header includes `dmub_dcn20.h` and declares `extern const struct dmub_srv_common_regs dmub_srv_dcn21_regs`.

## Control Flow And Data Flow

There is no runtime control flow in the header. Its declaration lets service creation code or generation-selection tables bind DCN21 hardware to the common DMUB register-access layer.

## State And Persistence Behavior

No state is owned here. The externally declared register table is immutable and generation-specific.

## Dependencies And Integration Points

The dependency on `dmub_dcn20.h` means DCN21 uses the common DCN20 register struct layout and function declarations. Integration is through `dmub_srv` hardware setup code that chooses `dmub_srv_dcn21_regs` for DCN21 ASICs.

## Risks And Edge Cases

Any DCN21-specific hardware behavior not represented by the common DCN20 functions would require additional declarations here. As written, this header assumes register-table substitution is sufficient.

## Test Signals

Build/link success for `dmub_srv_dcn21_regs` and runtime DMUB initialization on DCN21 hardware are the key signals.
