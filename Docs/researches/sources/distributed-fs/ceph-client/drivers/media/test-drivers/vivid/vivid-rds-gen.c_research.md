# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-rds-gen.c

Purpose: generates synthetic RDS/RBDS block streams for the Vivid radio receiver and transmitter loopback tests.

Important APIs and functions: exported functions are `vivid_rds_generate` and `vivid_rds_gen_fill`. Internal helpers include `vivid_get_di` for decoder information bits and time/date generation inside group 4A.

Control flow: `vivid_rds_gen_fill` populates PI, PTY, PS name, radiotext, traffic, stereo, and RBDS/RDS defaults based on frequency and alternate state. `vivid_rds_generate` fills 57 groups of four blocks: repeated group 0B for PI/PS, group 2A for radiotext, group 4A for current time, and group 15B filler elsewhere. It encodes block IDs in the `block` field and stores payload bytes in `lsb`/`msb`.

State and persistence: all generator state is in `struct vivid_rds_gen`: source fields plus the generated `v4l2_rds_data` block array. Time group contents are generated from current real time and timezone when generation runs.

Dependencies and integration points: depends on Linux time/string/kernel helpers and V4L2 RDS data definitions. It is called by radio common initialization and read/write loopback paths.

Risks: uses `sys_tz` and wall-clock time, so time blocks vary across systems and timezones. RDS group scheduling and payload layout are hand-encoded; off-by-one errors would be visible only to RDS decoders. Generated PS name derives from V4L2 low-frequency units, so unit mistakes in callers propagate into display text.

Test signals: decode generated RDS blocks for PI/PTY/PS/radiotext/time, alternate text toggling, RBDS vs RDS defaults, and block count/timing constants validate the generator.
