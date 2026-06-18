<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.h -->
# sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.h

## Purpose

`clk-icst.h` is the public local interface for ARM ICST clock wrappers.

## Important APIs, Types, And Functions

`enum icst_control_type` enumerates standard Versatile, Integrator AP/CP special cases, AP PCI, and IM-PD1 encodings. `struct clk_icst_desc` carries the ICST parameter table and VCO/lock register offsets. `icst_clk_register()` wraps a raw MMIO base; `icst_clk_setup()` accepts a caller-provided regmap and explicit control type.

## Control Flow

The header has no flow. Platform-specific setup files choose descriptors and control types, then call these registration helpers.

## State And Persistence Behavior

No state is stored here. The descriptor points to static parameters that implementation code clones for runtime use.

## Dependencies And Integration Points

It forward-declares `struct regmap` and relies on `struct device`, `struct clk`, and `struct icst_params` being visible to includers through existing Linux headers and `icst.h`.

## Risks And Test Signals

Risks are mismatched control type and register layout, or descriptors with wrong offsets. Build tests catch prototype drift; boot tests on Integrator/Versatile/IM-PD1 validate the right compatible routes to the right encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/versatile/clk-icst.h -->
