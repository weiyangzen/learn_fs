# sources/distributed-fs/ceph-client/drivers/pps/clients/Makefile

Purpose: maps PPS client Kconfig symbols to client object files.

Important rules: builds `pps-ktimer.o`, `pps-ldisc.o`, `pps_parport.o`, and `pps-gpio.o` from their respective `CONFIG_PPS_CLIENT_*` symbols. Debug config adds `-DDEBUG`.

Control flow/state: build-only file with no runtime state.

Dependencies/integration: object names define module names and must match Kconfig help text plus source module metadata.

Risks/test signals: run configured builds for each client as built-in and module; confirm debug flag and object naming, especially hyphen/underscore distinction for `pps_parport`.
