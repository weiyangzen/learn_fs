# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/si2168_priv.h

Purpose: Private SI2168 firmware names, runtime state, chip ids, and command buffer definition.

Important APIs/types/functions: firmware macros map A20, A30, B40, and D60 chips to file names. `struct si2168_dev` stores command mutex, mux, frontend, delivery/status, chip id/version, firmware name, TS mode, and active/warm/initialized/clock/inversion flags. `struct si2168_cmd` contains a 30-byte argument buffer and write/read lengths.

Control flow: `si2168.c` uses this state for probe, firmware loading, TS setup, tune/status commands, mux gate commands, sleep, and resume.

State and persistence: all runtime state is memory resident and reset by remove; firmware state is represented by `warm` and `initialized`.

Dependencies/integration: public `si2168.h`, DVB frontend, firmware loader, I2C mux, kernel helpers.

Risks: fixed `SI2168_ARGLEN` must exceed every firmware command; chip-id macros encode ASCII/numeric bytes and must match firmware query layout; warm-state logic depends on firmware version encoding.

Test signals: command length validation through firmware load, chip-id matching, resume/sleep warm transitions, mux creation/destruction.
