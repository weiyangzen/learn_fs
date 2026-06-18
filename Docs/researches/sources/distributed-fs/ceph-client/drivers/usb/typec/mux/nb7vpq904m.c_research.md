<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/nb7vpq904m.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/nb7vpq904m.c

## Purpose

`nb7vpq904m.c` drives the OnSemi NB7VPQ904M Type-C redriver. It registers a local orientation switch and retimer, chains orientation and mode changes to downstream Type-C switch/mux handles, configures channel equalization/output/gain/loss settings, and supports DP, DP+USB, USB, and safe states.

## Important APIs, Types, and Functions

`struct nb7vpq904m` contains GPIO/regulator/regmap handles, local switch/retimer, downstream switch/mux handles, lane-swap flag, mutex, orientation, mode, and SVID. Key functions are `nb7vpq904m_set_channel()`, `nb7vpq904m_set()`, `nb7vpq904m_sw_set()`, `nb7vpq904m_retimer_set()`, `nb7vpq904m_parse_data_lanes_mapping()`, `nb7vpq904m_probe()`, and `nb7vpq904m_remove()`.

## Control Flow

Probe initializes regmap and default state, obtains optional enable GPIO and VCC regulator, resolves downstream orientation switch and mode mux, parses endpoint `data-lanes` for normal or inverted mapping, powers/enables the chip, registers a DRM AUX bridge, then registers its switch and retimer. Switch set first forwards orientation downstream, then updates local routing under a mutex. Retimer set updates local mode/SVID, applies register programming, then forwards equivalent mux state downstream. Safe and USB states configure USB activity and AUX/CC defaults; DP states program all channels and AUX selection.

## State and Persistence Behavior

The driver caches mode/orientation/SVID and whether data lanes are inverted. Hardware register state persists only while the redriver is powered/enabled. Remove unregisters retimer/switch, disables GPIO/regulator, and drops downstream references.

## Dependencies and Integration Points

Dependencies include I2C, regmap, optional GPIO/regulator, OF graph endpoint lane mapping, DRM AUX bridge, Type-C switch/mux lookup, Type-C retimer registration, and DP altmode constants.

## Risks and Test Signals

Risks include continuing after regulator enable failure with only a warning, no chip-ID verification, fixed redriver tuning values, lane-mapping limited to exact four-lane normal/reversed arrays, and needing correct order when forwarding switch/mux state downstream. Test signals include inverted lane mapping, normal/reverse USB routing, DP C/E four-lane, DP D/F multi-function routing, downstream mux propagation, enable GPIO and regulator cleanup, and probe deferral for downstream switch/mux.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/nb7vpq904m.c -->
