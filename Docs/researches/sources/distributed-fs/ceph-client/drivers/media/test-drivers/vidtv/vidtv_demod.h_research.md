# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_demod.h

Purpose: data contracts for the virtual DVB demodulator.

Important APIs/types/functions: defines `struct vidtv_demod_cnr_to_qual_s`, `struct vidtv_demod_config`, and `struct vidtv_demod_state`.

Control flow: header only; used by bridge and demod implementation to pass simulation parameters and store frontend state.

State and persistence: `vidtv_demod_state` persists for the I2C client/frontend lifetime and stores current status and tuner CNR. Config probabilities are copied at probe.

Dependencies and integration points: includes DVB frontend types from Linux and media headers. Bridge supplies `vidtv_demod_config` as platform data and reads the resulting frontend from client data.

Risks: config fields are `u8`; module params are unsigned int in bridge and truncate when assigned, so values over 255 are not meaningful and probability logic expects 0-100.

Test signals: compile checks, bridge-to-demod platform data propagation, and frontend status behavior.
