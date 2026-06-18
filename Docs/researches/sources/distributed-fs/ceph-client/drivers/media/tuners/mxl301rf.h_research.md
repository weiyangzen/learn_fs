# sources/distributed-fs/ceph-client/drivers/media/tuners/mxl301rf.h

Purpose: public platform-data header for the MxL301RF I2C tuner driver.

Important APIs/types: includes `<media/dvb_frontend.h>` and defines `struct mxl301rf_config` containing only `struct dvb_frontend *fe`.

Control flow and integration: parent I2C-board registration passes this config as `client->dev.platform_data`; `mxl301rf_probe()` copies it, uses `fe` to install tuner ops, and stores private state in `fe->tuner_priv`.

State and persistence: no runtime state is declared here beyond the frontend pointer contract. All private state is in `mxl301rf.c`.

Dependencies: requires DVB frontend definitions and a parent driver that already knows how to initialize/configure the chip outside this header's contract.

Risks: the config cannot express I2C address, IF, clock, bandwidth capabilities, or init tables; those are assumed to come from I2C device registration and parent-specific firmware/init code. Because the C probe blindly dereferences platform data, callers must always provide a valid `mxl301rf_config`.

Test signals: probe registration with valid platform data, missing-platform-data robustness if fixed, and integration with the parent card driver that performs undisclosed initialization before tuner init.
