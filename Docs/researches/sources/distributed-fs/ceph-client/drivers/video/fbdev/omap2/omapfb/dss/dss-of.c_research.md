# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss-of.c

## Purpose

This file provides small OF graph helpers for OMAP DSS. It finds the device node owning a DSS port, reads a port number, and resolves the DSS source output connected to the first endpoint of a downstream device. The complete 78-line source was read.

## Important APIs, Types, and Functions

The public helpers are `dss_of_port_get_parent_device()`, `dss_of_port_get_port_number()`, and exported `omapdss_of_find_source_for_first_ep()`. They operate on `struct device_node`, OF graph endpoints and remote ports, and `struct omap_dss_device` returned by `omap_dss_find_output_by_port_node()`.

## Control Flow

`dss_of_port_get_parent_device()` walks up at most two parents from a port until it finds a node with a `compatible` property, returning a referenced node or `NULL`. `dss_of_port_get_port_number()` reads `reg`, defaulting to 0. `omapdss_of_find_source_for_first_ep()` gets endpoint 0 from a consumer node, finds its remote port, resolves that port to a registered OMAP DSS output, drops OF references, and returns either the output or `ERR_PTR(-EPROBE_DEFER)` if the output has not registered yet.

## State and Persistence Behavior

The file owns no persistent state. Its only state transitions are OF node reference count gets/puts. It returns borrowed DSS output pointers from the global OMAP DSS output registry.

## Dependencies and Integration Points

It depends on Linux OF graph APIs and the OMAP DSS output registry. Panel/encoder drivers use `omapdss_of_find_source_for_first_ep()` to discover their upstream DSS source, while DSS port registration code uses the port helpers to interpret graph layout.

## Risks and Edge Cases

Invalid or incomplete graphs return `-EINVAL`; a valid graph whose source driver has not registered returns `-EPROBE_DEFER`. Parent walking is intentionally shallow and assumes the DSS DT structure places a compatible node within two levels. Reference handling is small but important: endpoint and remote port references must be released on all paths.

## Test Signals

Test with valid panel-to-DSS graphs, missing endpoint 0, endpoints without remote ports, delayed DSS output registration, `reg` present and absent on ports, and graph layouts with intermediate `ports` nodes.
