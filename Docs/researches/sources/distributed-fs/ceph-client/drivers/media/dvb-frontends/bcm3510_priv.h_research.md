# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bcm3510_priv.h

Purpose: Defines private BCM3510 register bitfield layouts, HAB command IDs/message IDs, packed command/response structures, version constants, tuner command format, and logging helpers used by `bcm3510.c`.

Important APIs/types/functions: `bcm3510_register_value` is a union over one raw byte with named bitfield views for AP/HAB control/status, memory address/data, JDEC, revision, BER control, and tuner control registers. HAB structures include version info, external/internal tuner acquire, special symbol-rate/IF settings, auto reacquire, RF AGC selection, auto inversion, BERT control, tri-state, tuner control/data pairs, and status responses. Constants identify command groups such as `CMD_GET_VERSION_INFO`, `CMD_ACQUIRE`, `CMD_AUTO_PARAM`, `CMD_STATE_CONTROL`, `CMD_TUNE`, and `CMD_STATUS`.

Control flow: This header has no independent execution, but it defines the byte-level ABI for all `bcm3510_do_hab_cmd()` calls. `bcm3510.c` casts packed structures to byte buffers for HAB transmit/receive, and reads/writes `bcm3510_register_value` members before sending single-byte I2C register transactions.

State and persistence: Persistent-ish contract is the firmware/AP protocol: version constants `BCM3510_DEF_*` describe the expected firmware/script/config/demod versions. All structs are packed because they are sent directly over the Host Access Buffer and must match firmware layout.

Dependencies/integration: Consumed only by the BCM3510 implementation. It uses Linux integer types and relies on compiler bitfield layout for one-byte command/control fields.

Risks and test signals: Audit packed bitfield portability, command/message ID correctness, buffer sizes versus `MAX_XFER_SIZE`, and version checks. The mode constants are written with assignment syntax in `#define BCM3510_QAM16 = 0x01` style and are not used by the C file; using them later would be a compile hazard unless fixed.
