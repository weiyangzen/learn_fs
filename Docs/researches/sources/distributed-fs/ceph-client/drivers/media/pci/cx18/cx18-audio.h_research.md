<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.h

Purpose: Declares cx18 audio routing setup.

Important APIs/types: `cx18_audio_set_io(struct cx18 *cx)` selects and programs the current board audio path.

Control flow: Called by cx18 input/routing control paths when audio source selection must be applied.

State/persistence: No header state; implementation updates cx18 and subdevice hardware registers.

Dependencies/integration: Requires `struct cx18` from cx18 core.

Risks: Single API hides several hardware layers, so callers must ensure `cx->audio_input`, radio state, and board tables are valid first.

Test signals: Compile/link checks and audio switching paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-audio.h -->
