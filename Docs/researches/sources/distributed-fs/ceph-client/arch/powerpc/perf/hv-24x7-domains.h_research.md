
# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-24x7-domains.h

## Purpose

This macro include file defines the 24x7 performance domains and their metadata for enum generation, validation, sysfs formatting, and physical-domain permission checks.

## Important APIs, Types, And Functions

- `DOMAIN(PHYS_CHIP, 0x01, chip, true)`
- `DOMAIN(PHYS_CORE, 0x02, core, true)`
- `DOMAIN(VCPU_HOME_CORE, 0x03, vcpu, false)`
- `DOMAIN(VCPU_HOME_CHIP, 0x04, vcpu, false)`
- `DOMAIN(VCPU_HOME_NODE, 0x05, vcpu, false)`
- `DOMAIN(VCPU_REMOTE_NODE, 0x06, vcpu, false)`

Each entry carries an enum token, numeric hypervisor domain value, index-kind token, and physical/virtual flag.

## Control Flow

The file is included multiple times with different `DOMAIN` definitions. `hv-24x7.h` uses it to build `enum hv_perf_domains`; `hv-24x7.c` uses it to generate validation and physical-domain checks.

## State And Persistence

No state. It is a compile-time source of truth for 24x7 domain metadata.

## Dependencies And Integration Points

It integrates with `hv-24x7.h`, `hv-24x7.c`, perf sysfs format naming, and hcall request construction.

## Risks And Edge Cases

Because it is macro-included, field order and arity must remain stable across all consumers. The comment warns that catalog and hcall domain numbering are assumed to match and may need future changes.

## Test Signals

Build test all macro consumers, inspect `/sys/bus/event_source/devices/hv_24x7/interface/domains`, and validate physical vs virtual permission behavior.
