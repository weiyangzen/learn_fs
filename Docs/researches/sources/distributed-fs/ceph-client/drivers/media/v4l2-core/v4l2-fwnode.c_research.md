# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-fwnode.c

## Purpose
`v4l2-fwnode.c` parses firmware-node camera/video graph bindings and device properties into V4L2 media-bus, connector, async-subdevice, and sensor-registration structures. It supports Device Tree, ACPI, and software-node fwnodes, including CSI-2 D-PHY/C-PHY, CSI-1/CCP2, parallel, BT.656, DPI, analog connectors, orientation/rotation properties, and sensor-related references such as flash LEDs and focus lenses.

## Important APIs, Types, and Functions
Endpoint APIs are `v4l2_fwnode_endpoint_parse`, `v4l2_fwnode_endpoint_alloc_parse`, and `v4l2_fwnode_endpoint_free`. Link and connector APIs are `v4l2_fwnode_parse_link`, `v4l2_fwnode_put_link`, `v4l2_fwnode_connector_parse`, `v4l2_fwnode_connector_add_link`, and `v4l2_fwnode_connector_free`. Device/sensor APIs are `v4l2_fwnode_device_parse` and `v4l2_async_register_subdev_sensor`. Key internal helpers parse CSI-2, parallel, CSI-1, generic references, ACPI integer-property references, and common sensor references.

## Control Flow
Endpoint parsing begins by reading the fwnode `bus-type`, converting it to a V4L2 media-bus type, reconciling it with any caller-supplied expected `vep->bus_type`, then dispatching to bus-specific parsers. CSI-2 parsing handles default lane mapping, `data-lanes`, duplicate lane detection, optional `clock-lanes`, `lane-polarities`, C-PHY `line-orders`, and `clock-noncontinuous`. Invalid lane-polarity or line-order counts fail with `-EINVAL`; duplicate lanes fall back to default mapping where possible. Parallel/BT.656 parsing reads polarity, pclk, data-active, slave/master, bus-width, data-shift, sync-on-green, and data-enable properties, then infers parallel vs BT.656 when the bus type was unknown. CSI-1/CCP2 parsing reads clock/data lane and strobe properties.

`v4l2_fwnode_endpoint_alloc_parse` extends endpoint parsing by allocating and reading `link-frequencies`; callers must free with `v4l2_fwnode_endpoint_free`. Link parsing obtains the local port parent and remote endpoint/parent from graph helpers and stores local/remote ids and ports; `v4l2_fwnode_put_link` releases both parent refs. Connector parsing finds a known connector compatible string on either side of the graph edge, reads label and analog SDTV standards, and `connector_add_link` appends parsed graph links to the connector link list.

Device parsing reads `orientation` and `rotation`, validates allowed ranges, and stores unset sentinels if absent. Sensor async registration allocates a notifier, initializes it for the subdevice, obtains a privacy LED, parses sensor references (`flash-leds`, `mipi-img-flash-leds`, `lens-focus`, `mipi-img-lens-focus`) via generic fwnode references or ACPI integer-property traversal, registers the notifier, then registers the subdevice. Failure unwinds notifier registration, privacy LED, cleanup, and allocation.

## State and Persistence Behavior
The file mutates caller-provided endpoint, connector, device-property, link, and notifier structures. It allocates link-frequency arrays, connector labels/links, async notifier storage, and fwnode references that must be released by matching free/put/cleanup functions. There is no persistent storage beyond firmware descriptions supplied by platform firmware.

## Dependencies and Integration Points
It depends on firmware property APIs, fwnode graph helpers, ACPI node detection, V4L2 async notifier APIs, V4L2 subdevice privacy LED helpers, media-bus configuration structs, and kernel memory management. It is a bridge between firmware graph descriptions and the runtime media graph used by camera bridge/sensor drivers.

## Risks
Reference-count handling is the main risk: every graph parent, endpoint, child fwnode, connector label, link, and notifier allocation has a matching cleanup path. ACPI integer reference traversal is complex and can fail differently for out-of-bounds vs malformed properties. Bus-type guessing may choose CSI-2 or parallel based on partial properties, so ambiguous firmware can produce surprising defaults. Duplicate CSI lanes fall back to defaults, which may hide firmware mistakes. Sensor registration has several failure stages that must keep privacy LED and notifier ownership consistent.

## Test Signals
Test DT and ACPI endpoint parsing for CSI-2 D-PHY, C-PHY, CSI-1/CCP2, parallel, BT.656, unknown/guessed bus types, invalid lane counts, duplicate lanes, link-frequency allocation/free, connector parse/add/free with labels and SDTV standards, orientation/rotation validation, sensor async registration with duplicate references, missing references, privacy LED failures, and notifier/subdevice registration unwind.
