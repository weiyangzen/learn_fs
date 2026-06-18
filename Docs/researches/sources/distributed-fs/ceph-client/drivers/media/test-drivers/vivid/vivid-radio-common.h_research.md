# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-common.h

Purpose: defines shared radio frequency ranges, band identifiers, and common frequency/RDS helper declarations for Vivid radio RX/TX.

Important APIs and types: FM, AM, and SW ranges are defined in V4L2 low-frequency units (`kHz * 16`). `enum { BAND_FM, BAND_AM, BAND_SW, TOT_BANDS }` indexes `vivid_radio_bands`. Public helpers are `vivid_radio_g_frequency`, `vivid_radio_s_frequency`, and `vivid_radio_rds_init`.

Control flow: RX and TX ioctl implementations call the common helpers to avoid duplicating range handling and RDS setup.

State and persistence: no header-owned state. It defines constants used to mutate per-device frequency and RDS state.

Dependencies and integration points: consumers need V4L2 frequency-band types and Vivid device declarations.

Risks: frequency units must remain consistent with V4L2 radio APIs; callers passing raw Hz or kHz would get incorrect clamping.

Test signals: compile coverage plus frequency ioctl tests at all range boundaries validate this header.
