# sources/distributed-fs/ceph-client/net/lapb/Kconfig

## Purpose
This Kconfig entry exposes the LAPB data link driver used for reliable Link Access Procedure Balanced service, primarily as the lower data-link layer for X.25.

## Important APIs, Types, and Functions
The file defines the tristate symbol `LAPB`. Its help text describes LAPB as a reliable point-to-point data-link service and notes that Linux support is currently oriented around LAPB over Ethernet.

## Control Flow
The symbol controls whether the LAPB module is compiled. When enabled, the directory Makefile links the protocol implementation into `lapb.o`.

## State and Persistence
No runtime state exists in the Kconfig file. Its selected value persists as kernel configuration and determines whether the exported LAPB API is present.

## Dependencies and Integration Points
The symbol is intended for users of X.25/LAPB-over-Ethernet drivers and references `Documentation/networking/lapb-module.rst` for operational details.

## Risks and Edge Cases
Because the symbol is tristate and exports functions to device drivers, mismatched module/built-in configurations can affect link dependencies. Users may assume support for specialized X.21 hardware despite the help text noting Linux's Ethernet-oriented support.

## Test Signals
Build tests should cover `LAPB=n`, built-in, and module modes, plus dependent LAPB-over-Ethernet/X.25 configurations.
