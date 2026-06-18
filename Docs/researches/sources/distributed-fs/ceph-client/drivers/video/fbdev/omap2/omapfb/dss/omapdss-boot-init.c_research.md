# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/omapdss-boot-init.c

## Purpose
`omapdss-boot-init.c` is an early boot compatibility shim for legacy OMAP DSS panel/encoder drivers. It walks the display graph and rewrites non-root connected display node `compatible` strings by prepending `omapdss,`, allowing generic-looking DT data to bind to OMAPDSS-specific drivers.

## Important APIs, types, and functions
The file is driven by `subsys_initcall(omapdss_boot_init)`. Important helpers are `omapdss_count_strings`, `omapdss_update_prop`, `omapdss_prefix_strcpy`, `omapdss_omapify_node`, `omapdss_add_to_list`, `omapdss_list_contains`, and `omapdss_walk_device`. `struct dss_conv_node` tracks walked device nodes and whether they are graph roots.

## Control Flow
Boot init finds an available DSS root compatible with OMAP2/3/4/5 or DRA7. It walks the DSS node and available DSS children through OF graph endpoints, collecting each reachable node once. During cleanup of the list, it skips root nodes and rewrites non-root nodes with valid, unprefixed `compatible` properties. The rewrite allocates a new property and calls `of_update_property`.

## State and Persistence
State is early-init-only: `dss_conv_list` and allocated `dss_conv_node` entries are freed before returning. Rewritten OF properties persist in the live device tree for the rest of the boot, but not across reboot.

## Dependencies and Integration Points
It depends on OF graph APIs, device tree node availability, and OMAP DSS compatible strings. Its output affects later platform driver matching for panels and encoders.

## Risks
The code intentionally mutates the live device tree, which can surprise generic panel drivers. Allocation failures silently skip property/list updates. The walker relies on graph topology and may miss devices not reachable through endpoints. `omapdss_count_strings` assumes a valid string-list property after a first string-length check.

## Test Signals
Boot DTs with legacy and already-prefixed compatible strings, disconnected or unavailable graph nodes, multiple compatible strings, missing `port`/`ports`, graph cycles, allocation failure simulation, and driver binding order before panel probes are the key signals.
