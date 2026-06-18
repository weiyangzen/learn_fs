# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/anysee.h

Purpose: This header captures the Anysee driver's private protocol and board-state definitions. It defines command opcodes, the private state shape, known hardware IDs, GPIO register addresses, and a reverse-engineered USB API note block that explains the 64-byte transaction protocol used by `anysee.c`.

Important APIs/types: `enum cmd` defines command values for I2C read/write, register read/write, stream control, LED/IR control, IR code polling, hardware-info query, smartcard command placeholder, and CI command. `struct anysee_state` stores the 64-byte command/reply buffer, packet sequence, PCB hardware ID, one managed I2C client slot, frontend and feature flags, the `dvb_ca_en50221` object, and the jiffies deadline used to report CAM ready. `ANYSEE_HW_*` macros map numeric PCB IDs to E30/E7 model families. `REG_IO*` and `REG_OE*` macros identify Cypress port and output-enable registers used for demod/tuner power and signal routing.

Control flow support: The header's command values are consumed by `anysee_ctrl_msg()` and its helper APIs. Hardware IDs drive the large frontend/tuner switch in `anysee_frontend_attach()` and `anysee_tuner_attach()`. Register macros drive `frontend_ctrl`, CI reset/shutdown/TS enable, tuner-gate handling, and initial LED/IR configuration.

State and persistence behavior: The definitions describe runtime state and volatile USB-controller registers. The reverse-engineered protocol comments identify sequence byte offset 60 and "previous reply/current reply" behavior, which explains why the implementation reads two replies for every command. The smart-card command is documented but not implemented as persistent support.

Dependencies and integration points: It includes `dvb_usb.h` and EN50221 CI definitions. The state structure is allocated by the v2 core through `anysee_props.size_of_priv`, and the CI object is registered against the DVB adapter when supported hardware is detected.

Risks: The header contains many magic numbers from reverse engineering. The protocol documentation appears to have a few offset/name inconsistencies, so implementation behavior should be treated as authoritative. `ANYSEE_I2C_CLIENT_MAX` is one, which is sufficient for the current TDA18212 client use but constrains future multi-client additions. Hardware IDs outside the listed set will fail attach and ask users to report them.

Test signals: Compile tests should validate command enum names against `anysee.c`. Runtime signs are stable sequence handling, correct model ID decoding, expected GPIO route switching, and CI/RC behaviors matching the documented packet layouts.
