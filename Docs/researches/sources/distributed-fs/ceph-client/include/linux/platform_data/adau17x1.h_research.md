# sources/distributed-fs/ceph-client/include/linux/platform_data/adau17x1.h

Purpose: provides platform data for Analog Devices ADAU17x1-family audio codecs, describing microphone bias, jack/digital-mic pin use, debounce, polarity, output topology, and differential input wiring.

Important APIs and types: `enum adau17x1_micbias_voltage` selects 0.90 or 0.65 AVDD microphone bias. `enum adau1761_digmic_jackdet_pin_mode` selects disabled, digital microphone, or jack detect for the shared pin. `enum adau1761_jackdetect_debounce_time` chooses 5/10/20/40 ms. `enum adau1761_output_mode` selects headphone, capless headphone, or line output. `struct adau1761_platform_data` carries input differential, line/headphone modes, shared-pin mode, debounce, jackdetect polarity, and micbias. `struct adau1781_platform_data` carries left/right differential input flags, digital mic selection, and micbias.

Control flow: board code supplies codec platform data at device creation; the ASoC codec driver consumes it during probe to configure DAPM routes, jack detect, bias voltage, pin modes, and analog output registers.

State and persistence: platform data is static board/audio-jack topology. Runtime codec register/cache state lives in the driver and hardware and is typically restored through regmap/ASoC resume.

Dependencies and integration points: integrates legacy board files with ASoC codec drivers, DAPM routing, jack detection, microphone bias, and machine-driver topology.

Risks and test signals: risks include choosing mutually exclusive shared-pin modes incorrectly, wrong active-low jack polarity, differential/single-ended mismatch, and output mode mismatch causing audio distortion or missing routes. Test codec probe, DAPM route availability, headphone/line output, jack insertion/removal with debounce, digital mic capture, suspend/resume, and platform-data versus firmware-property parity.
