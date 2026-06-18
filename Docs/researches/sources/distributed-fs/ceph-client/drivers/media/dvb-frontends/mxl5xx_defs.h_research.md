<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_defs.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_defs.h

## Purpose
`mxl5xx_defs.h` defines the MaxLinear Hydra firmware command protocol, command payload structs, device/SKU enums, demod/tuner/TS configuration enums, MBIN firmware image headers, and helper macros used by `mxl5xx.c`.

## Important APIs, Types, And Functions
The header provides `enum MXL_HYDRA_HOST_CMD_ID_E` for firmware command ids, PLID constants for register and command reads/writes, max command and block sizes, MBIN file/segment structures, `BUILD_HYDRA_CMD()`, register-field helpers, SKU/device enums, demod/tuner IDs, broadcast standard/FEC/modulation/spectrum/rolloff/pilot enums, channel parameter offsets, TS PID/mux/MPEG output enums and structs, firmware download structures, tuner activation command payloads, and demod tune/scramble/abort payloads. `MXL_HYDRA_DEMOD_PARAM_T` is the main tuning payload, and `MXL_HYDRA_MPEGOUT_PARAM_T` is the main TS output configuration payload.

## Control Flow
The header contains no executable functions except the `BUILD_HYDRA_CMD()` macro. That macro builds the Hydra I2C command frame with PLID, length, payload size, command id, endian conversion, and payload copy. `mxl5xx.c` uses these constants and structs in firmware download, SKU configuration, tuner activation, demod tune, scramble-code programming, and TS output configuration.

## State And Persistence
The structures describe wire-format firmware messages and firmware image layout rather than kernel-owned persistent state. Their field order and sizes form an ABI with MaxLinear firmware. MBIN headers also define the persistent firmware file format expected by the loader.

## Dependencies And Integration Points
The header assumes Linux integer types and that `convert_endian()` is visible before `BUILD_HYDRA_CMD()` is expanded in `mxl5xx.c`. It integrates tightly with `mxl5xx_regs.h` address constants and with MaxLinear firmware semantics for command IDs, SKU values, and TS mux behavior.

## Risks
Changing enum values, struct field order, command IDs, or max lengths can break the firmware protocol. `BUILD_HYDRA_CMD()` mutates the source payload when endian conversion is enabled, so callers must not assume untouched input data in a big-endian configuration. Several protocol names encode vendor assumptions and some comments indicate incomplete or device-specific support; adding features should be checked against firmware documentation.

## Test Signals
Compile coverage on little- and big-endian targets, firmware download with valid/invalid MBIN headers and checksums, command construction tests against known byte sequences, and tuning/TS-output tests for every supported Hydra SKU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/mxl5xx_defs.h -->
