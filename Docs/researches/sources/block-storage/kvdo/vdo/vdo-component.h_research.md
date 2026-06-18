# File Research: sources/block-storage/kvdo/vdo/vdo-component.h

This header defines the persisted VDO service component: `struct vdo_config` and `struct vdo_component`. The config stores logical block count, physical block count, slab size, recovery journal size, and slab journal block count. The component stores VDO state, complete/read-only recovery counters, config, and nonce.

It declares encoded-size, encode, decode, and config-validation functions used by the super-block component-state layer.
