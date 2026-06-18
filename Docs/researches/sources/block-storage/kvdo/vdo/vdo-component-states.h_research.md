# File Research: sources/block-storage/kvdo/vdo/vdo-component-states.h

This header declares the aggregate `struct vdo_component_states` persisted in the super block: release version, volume version, VDO component, block map state, recovery journal state, slab depot state, and fixed layout.

It exposes destroy, decode, validate, and encode functions, plus the external volume version constant `VDO_VOLUME_VERSION_67_0`. Comments document that volume major/minor versions must change when on-disk representations change.
