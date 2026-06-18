# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp.h

Purpose: shared sun6i ISP header defining device-wide structures, tables, variant data, and core helper declarations.

Important APIs/types: `enum sun6i_isp_port` identifies CSI0/CSI1 graph ports. `struct sun6i_isp_buffer` wraps vb2 buffers with a list node. `struct sun6i_isp_v4l2` holds V4L2/media devices. `struct sun6i_isp_table/tables` describe coherent DMA tables for load/save/LUT/DRC/stats. `struct sun6i_isp_device` aggregates subcomponents, regmap, clocks, reset, and global state lock. `struct sun6i_isp_variant` provides table sizes. Helper declarations expose load-table access, address conversion, state update, and table register configuration.

Control flow: no implementation; all submodules include this header and share the same `sun6i_isp_device`.

State and persistence: defines device lifetime state and frame-to-frame load-table state. Subcomponent headers are included so the aggregate struct embeds full proc/capture/params state.

Dependencies/integration: depends on V4L2 device and vb2-v4l2 headers plus local capture/params/proc headers.

Risks: circular inclusion pressure is high because this header embeds subcomponent structs and subcomponent headers forward-declare `sun6i_isp_device`. The declaration `sun6i_isp_address_value()` appears while source uses the macro `SUN6I_ISP_ADDR_VALUE`; ensure implementation exists elsewhere or declaration is stale.

Test signals: build coverage, static analysis for include cycles/stale declarations, and runtime validation that embedded subcomponent state is initialized before use.
