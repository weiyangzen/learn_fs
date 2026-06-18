# sources/distributed-fs/ceph-client/drivers/soc/apple/tunable.c

## Purpose
This helper parses and applies Apple Silicon hardware tunables supplied by firmware or boot stages through device tree properties.

## Important APIs, Types, And Functions
Exports are `devm_apple_tunable_parse()` and `apple_tunable_apply()`. The public `struct apple_tunable` contains entries with MMIO offset, mask, and value.

## Control Flow
Parsing validates the MMIO resource is at least one word, finds the named DT property, requires property length to be triples of 32-bit values, allocates a flexible-array tunable, reads offset/mask/value triples, and rejects unaligned or out-of-resource offsets. Applying iterates entries, reads the current register value, clears masked bits, ORs the desired value, and writes only when changed.

## State, Persistence, And Dependencies
State is a device-managed parsed tunable object. Hardware persistence is whatever register effects the writes have. Dependencies include OF property helpers, overflow-safe `struct_size()`, MMIO read/write, and a public tunable header.

## Integration Points
Apple platform drivers can parse device-specific register adjustments and apply them after mapping hardware registers.

## Risks
The parser does not validate that `value` is contained within `mask`; it will set any bits present in value. Applying is not locked, so drivers must serialize against other register programming. Incorrect firmware properties can alter hardware behavior broadly despite offset range checks.

## Test Signals
Test missing property, malformed length, offset alignment, offset beyond resource, successful parse, idempotent apply, and value/mask interactions on a fake MMIO region.
