# sources/cloud-native/ostree/man/ostree-find-remotes.xml

Purpose: documents `ostree find-remotes`, which discovers remotes that advertise refs for peer-to-peer or removable-media pulls.

Important APIs/types: command takes collection/ref inputs; options cover cache, finder, and output/pull behavior in the page.

Control flow: queries configured discovery mechanisms, removable media, LAN/P2P sources, or cache locations for matching collection/ref pairs and reports usable remotes.

State and persistence: primarily read-only discovery; may use caches depending on options.

Dependencies and integration: integrated with collection IDs, `create-usb`, remote config, Avahi/P2P support when built, and pull command workflows.

Risks and test signals: risks include collection-id mismatches, discovery backend availability, and stale cache results. Signals are tests with local USB-style repos, configured remotes, and Avahi-enabled builds.
