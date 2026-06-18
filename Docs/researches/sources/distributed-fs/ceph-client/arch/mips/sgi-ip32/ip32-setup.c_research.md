# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-setup.c

Purpose: IP32 basic setup and timer calibration. It installs bus-error handling, optionally captures the Ethernet MAC from ARCS, chooses serial console, and calibrates CP0 count against the CRIME timer.

Important APIs and control flow: optional `str2eaddr()` parses the ARCS `eaddr` string into `o2meth_eaddr`. `plat_time_init()` zeroes CP0 count and CRIME timer, waits 10 ms worth of CRIME master cycles, computes `mips_hpt_frequency`, and logs CPU MHz. `plat_mem_setup()` sets `board_be_init`, reads MAC/console ARCS variables under config guards, and adds a ttyS preferred console with optional `dbaud`.

State, persistence, and integration: state includes `board_be_init`, `mips_hpt_frequency`, optional Ethernet MAC buffer, and console preference. Dependencies include CRIME timer registers, ARCS variables, and CRIME/MACE memory setup having occurred before timer access. Risks include busy-wait calibration, no validation for missing `eaddr` before parsing, and firmware string assumptions. Test signals are CPU MHz log, correct MAC, preferred serial console, and bus-error handler installation.
