# sources/distributed-fs/ceph-client/sound/soc/sof/intel/hda-probes.c

Purpose: registers an HDA-backed SOF probes client that uses compressed capture streams for firmware/audio probes. It adapts the generic SOF probes client interface to HDA host DMA allocation, setup, trigger, and position accounting.

Important APIs: `hda_probes_register()` and `hda_probes_unregister()` register/unregister the `hda-probes` SOF client. `hda_probes_compr_startup()` obtains a capture/playback stream with `hda_dsp_stream_get()` and returns the stream tag. `hda_probes_compr_set_params()` programs S32 sample width, sample rate, channels, buffer, and period fields before calling `hda_dsp_stream_hw_params()`. `hda_probes_compr_trigger()` delegates to HDA stream trigger, and `hda_probes_compr_pointer()` reports `curr_pos`.

Control flow: startup allocates and binds `cstream->runtime->private_data`; set_params configures DMA; trigger starts/stops the descriptor; pointer is updated from interrupt-side compressed-byte accounting in `hda-stream.c`; shutdown puts the stream and clears private pointers.

State and persistence: runtime state is the compressed stream's private `hdac_ext_stream`, `hdac_stream->cstream`, `curr_pos`, and BDL/buffer fields. No persistent configuration is stored.

Dependencies and integration: depends on SOF client-probes, ALSA compressed stream APIs, and HDA stream exports. It is pulled into HDA client registration from `hda.c`.

Risks and test signals: risks include stream exhaustion (`-EBUSY`), format assumptions because compressed params lack bit depth, stale `private_data` on error, and correct `curr_pos` wrap accounting. Test client registration, probe capture start/stop, fragment elapsed callbacks, shutdown-after-failed-set_params, and stream reuse after unregister.
