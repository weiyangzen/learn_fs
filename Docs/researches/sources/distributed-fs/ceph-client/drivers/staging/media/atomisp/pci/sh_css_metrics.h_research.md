# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_metrics.h

Purpose: `sh_css_metrics.h` defines CSS runtime metrics structures and declares the metrics control/sampling functions. It is the public-private contract used by pipeline code to track frame counts and optional PC histograms.

Important APIs/types/functions: `struct sh_css_pc_histogram` stores length plus `run`, `stall`, and `msink` arrays. `struct sh_css_binary_metrics` stores binary mode/id, ISP and SP histograms, and next pointer. `struct ia_css_frame_metrics` holds `num_frames`. `struct sh_css_metrics` combines a linked list of binary metrics and frame metrics. Declared functions are `sh_css_metrics_enable_pc_histogram()`, `sh_css_metrics_start_frame()`, `sh_css_metrics_start_binary()`, and `sh_css_metrics_sample_pcs()`.

Control flow and state: this header has no logic. The extern `sh_css_metrics` represents persistent process/driver metrics state managed by `sh_css_metrics.c`.

Dependencies and integration: it includes `type_support.h` and then `ia_css_types.h` after the structure definitions because `ia_css_binary.h` depends on metrics definitions. Users include it when embedding `sh_css_binary_metrics` in binary descriptors or invoking sampling hooks.

Risks: the histogram arrays are raw pointers with no ownership annotations in the type definition, so lifetime management is implicit. Linked-list ownership of `sh_css_binary_metrics` also depends on caller-provided storage remaining valid while metrics are collected.

Test signals: compile tests should confirm include ordering does not create circular dependencies. Runtime tests should verify metrics remain valid across binary lifetimes and are reset or freed by the owning code path.
