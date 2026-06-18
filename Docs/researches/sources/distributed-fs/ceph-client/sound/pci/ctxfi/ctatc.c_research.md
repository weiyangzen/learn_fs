# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctatc.c

Purpose: central Audio Transport Controller (ATC) orchestration layer for ctxfi. It identifies the card, initializes chip-specific hardware, creates resource managers, builds the internal audio topology, services PCM prepare/start/stop/position, controls input/output routing, handles S/PDIF passthrough, and supports PM resume.

Important APIs and types: exported entry points are `ct_atc_create` and `ct_atc_create_alsa_devs`. Major internal APIs include `atc_pcm_playback_prepare/start/position`, `atc_pcm_capture_prepare/start/position`, `spdif_passthru_playback_prepare`, routing controls (`select_line_in`, `select_mic_in`, `line_*_unmute`, `spdif_*`), `atc_get_resources`, `atc_connect_resources`, and `atc_release_resources`.

Control flow: creation copies `atc_preset`, identifies model via PCI quirks, creates VM, hardware object, resource managers, mixer, persistent DAIO/SRC/SRCIMP/SUM resources, connects DAIs/DAOs to mixer ports, creates timer, and registers a low-level ALSA device for cleanup. Playback prepare releases old stream resources, allocates MEMRD SRC plus AMIXERs, maps the DMA buffer into device VM, and connects SRC outputs to PCM SUMs. Capture prepare may allocate SRC conversion stages, SRCIMPs, AMIXERs, and a mono SUM, then connects mixer outputs to a MEMWR SRC. Starts program SRC addresses/states and synchronously enable SRCs.

State and persistence: `struct ct_atc` stores hardware, VM, mixer, resource managers, DAIO table, persistent SRC/SRCIMP inputs, PCM SUMs, timer, PLL rate, model/capabilities, and stream resources in `struct ct_atc_pcm`. Runtime state is hardware graph allocation plus device virtual memory mappings. PM suspend releases resources and stops hardware; resume reinitializes hardware and rebuilds topology.

Dependencies and integration: integrates `ctpcm`, `ctmixer`, `ctsrc`, `ctamixer`, `ctdaio`, `cttimer`, `ctvmem`, and chip-specific `struct hw` callbacks. ALSA PCM/mixer front ends call into this operation table.

Risks and test signals: graph construction has many partial-allocation paths; `atc_release_resources` is the critical cleanup backstop. Rate conversion logic depends on pitch thresholds and limited ROM selections. S/PDIF passthrough temporarily reinitializes SPDIF DAO and PLL. Tests should cover card model detection, all ALSA device creation, playback/capture at 32/44.1/48/96/192 kHz where supported, mono and multichannel capture, S/PDIF passthrough toggle, output switches, resource exhaustion, and suspend/resume graph rebuild.
