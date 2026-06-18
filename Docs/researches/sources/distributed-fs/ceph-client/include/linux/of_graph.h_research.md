<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_graph.h -->
# sources/distributed-fs/ceph-client/include/linux/of_graph.h

## Purpose
This header declares helpers for parsing OF graph bindings, where devices expose ports and endpoints connected by remote-endpoint phandles.

## Important APIs, types, and functions
`struct of_endpoint` stores parsed port id, endpoint id, and local endpoint node. Iterators include `for_each_endpoint_of_node()`, `for_each_of_graph_port()`, and `for_each_of_graph_port_endpoint()`. APIs include `of_graph_is_present()`, `of_graph_parse_endpoint()`, endpoint/port count helpers, `of_graph_get_port_by_id()`, next endpoint/port helpers, endpoint lookup by regs, remote endpoint/port/parent lookup, and `of_graph_get_remote_node()`.

## Control flow
Drivers inspect whether a graph is present, iterate ports/endpoints, parse each endpoint's `reg` values, and follow `remote-endpoint` links to the peer endpoint, port, or device node. Scoped iterators use cleanup-based `of_node_put()`; non-scoped endpoint iteration requires manual put when leaving early.

## State and persistence
No state is stored here. Returned nodes are references into the live OF tree whose lifetime is controlled by node reference counts.

## Dependencies and integration points
It depends on OF nodes, cleanup annotations, errno, and graph binding conventions. It integrates display, media, audio, and interconnect-style drivers that need DT-described topology.

## Risks and test signals
Risks include leaked node refs on early loop exit, malformed bidirectional graph links, missing `reg` properties, port-vs-ports container ambiguity, and assuming unique endpoint ids. Test graph parsing with single and multi-port devices, broken remote links, scoped iterator cleanup, disabled `CONFIG_OF`, and media/display pipeline probe ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_graph.h -->
