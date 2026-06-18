# sources/distributed-fs/ceph-client/sound/aoa/codecs/Makefile

## Purpose

This Makefile builds the AOA codec modules for Onyx, TAS, and Toonie.

## Important APIs, types, and functions

It maps `snd-aoa-codec-onyx-y := onyx.o`, `snd-aoa-codec-tas-y := tas.o`, and `snd-aoa-codec-toonie-y := toonie.o`, then adds each object according to its config symbol.

## Control Flow

Kbuild conditionally builds codec modules when selected in Kconfig.

## State and Persistence

No runtime state exists here.

## Dependencies and Integration Points

It is consumed by AOA directory recursion and produces module names that layout fabric can request.

## Risks and Test Signals

Risks are build-wiring issues. Tests should build each codec as module and built-in, verifying module aliases and request_module names line up.
