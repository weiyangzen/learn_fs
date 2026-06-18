# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmux.h

## Purpose
Public AUDMUX interface for i.MX machine drivers. It exposes port constants, bitfield macros, and configuration function prototypes.

## APIs, Types, and Functions
Defines MX31 port numbers such as `MX31_AUDMUX_PORT1_SSI0` through SSI pins port 7, V2 PTCR/PDCR bit builders for sync, clock/frame direction and selection, RX data selection, and prototypes for `imx_audmux_v1_configure_port()` and `imx_audmux_v2_configure_port()`.

## Control Flow, State, and Persistence
No runtime state. The header encodes how callers build the PCR/PTCR/PDCR values persisted by `imx-audmux.c` into hardware registers and its static cache.

## Dependencies and Integration
Used by SSI-based board drivers including ES8328 and SGTL5000 machine drivers. The prototypes are backed by exported symbols in `imx-audmux.c`.

## Risks and Test Signals
Risks are off-by-one port handling in callers because hardware manuals number ports from 1 while the API uses zero-based indexes, and incorrect bitfield composition causing swapped clocks or data sources. Test signals are build coverage of users and working audio after configuring internal and external mux ports.
