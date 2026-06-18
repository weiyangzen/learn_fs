# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/out.h

## Purpose
This header defines cached output state and inline helpers for ZL3073x output mode, signal format, enablement, N-div, differential status, and synthesizer selection.

## Important APIs and types
`struct zl3073x_out` separates mutable config fields (`div`, `width`, `esync_n_period`, `esync_n_width`, `phase_comp`, `mode`) from invariant `ctrl`. Inline helpers get/set clock type, decode signal format, test differential formats, test output enablement, detect N-div formats, and get the attached synth.

## Control flow and integration
The inline helpers are used by property parsing, DPLL pin registration, output frequency computation, esync control, and output state commits.

## Risks and tests
Signal-format classification directly controls whether N pins are registered and how output frequencies are computed. Tests should cover LVDS/differential/low-VCM, 1P/1N, normal two-output, inverted, and N-div formats.
