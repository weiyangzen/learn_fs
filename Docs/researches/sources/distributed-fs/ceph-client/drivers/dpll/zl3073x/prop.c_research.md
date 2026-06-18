# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/prop.c

## Purpose
This file derives DPLL device and pin properties from cached hardware state plus firmware-node metadata. It supplies labels, pin types, capabilities, supported frequency ranges, esync-control flags, and DPLL channel type.

## Important APIs
`zl3073x_pin_props_get()` allocates and fills a `struct zl3073x_pin_props` for a given input/output pin. `zl3073x_pin_props_put()` releases it. `zl3073x_prop_dpll_type_get()` maps the optional `dpll-types` device property to `DPLL_TYPE_PPS` or `DPLL_TYPE_EEC`. Internal helpers validate frequencies, synthesize package labels, and locate per-pin fwnodes.

## Control flow
Property creation starts with defaults: input pins are external references with state/priority capabilities; output pins default to GNSS and get phase granularity from half the driving synth period. It generates labels such as `REF0P`, `REF0`, `OUT1N`, or `OUT1` depending on differential state. It optionally locates `input-pins` or `output-pins` child nodes by `reg`, then reads `label`, `connection-type`, `esync-control`, and `supported-frequencies-hz`. Supported frequencies become exact min=max DPLL ranges, always including the current frequency, and invalid firmware-provided frequencies are warned and skipped.

## State and persistence
Returned property objects are transient heap allocations used during pin registration. Firmware-node handles are reference-counted until `zl3073x_pin_props_put()`.

## Dependencies and integration points
The file depends on cached ref/out/synth state from `core.h`, frequency factorization from `ref.c`, firmware-node/property APIs, and Linux DPLL property structures. `dpll.c` consumes these properties during pin registration.

## Risks and tests
Invalid firmware frequency lists must not prevent registration except for allocation failures. Output frequency validation divides by requested frequency, so zero frequencies from firmware are risky and should be validated by tests. Tests should cover missing nodes, labels, connection type mapping, unknown types, esync flag, frequency filtering, differential labels, and channel type defaults.
