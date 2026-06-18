# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-radio-common.c

Purpose: provides shared AM/FM/SW radio frequency-band handling, signal-quality emulation, and RDS generator initialization for Vivid radio receiver and transmitter nodes.

Important APIs and functions: exports `vivid_radio_bands`, `vivid_radio_rds_init`, `vivid_radio_g_frequency`, and `vivid_radio_s_frequency`. `vivid_radio_calc_sig_qual` is the internal quality and RDS-looping calculator.

Control flow: set-frequency selects the nearest supported band, clamps the requested frequency, stores it through the caller-provided pointer, recalculates signal quality against ideal channels and optional transmitter frequency, and reinitializes RDS data. RDS initialization either copies TX RDS controls when radio loopback is active, leaves block-I/O TX-provided data alone, or generates standard alternate RDS/RBDS content from frequency. When RX RDS controls are enabled, it mirrors generated values into RX RDS controls.

State and persistence: state is volatile in `struct vivid_dev`: RX/TX frequencies, `radio_rx_sig_qual`, `radio_rds_loop`, RDS generator contents, RDS alternate toggle, and V4L2 RDS control values. Generated RDS blocks persist until regenerated or overwritten by TX block I/O.

Dependencies and integration points: depends on V4L2 tuner/frequency definitions, Vivid core, control helpers, and `vivid-rds-gen.c`. It is used by both receiver and transmitter ioctl paths.

Risks: `vivid_radio_s_frequency` updates `*pfreq` before calling `vivid_radio_calc_sig_qual`, so quality calculation depends on the correct field pointer being passed. RDS loop state depends on both RX and TX frequencies and can clear generated data when switching modes. The band selection uses midpoint thresholds rather than explicit requested modulation.

Test signals: set/get frequency for AM/SW/FM, clamp boundaries, signal strength near/off channel, RX/TX same-frequency loopback, RDS controls vs block I/O, and alternate radiotext behavior are primary tests.
