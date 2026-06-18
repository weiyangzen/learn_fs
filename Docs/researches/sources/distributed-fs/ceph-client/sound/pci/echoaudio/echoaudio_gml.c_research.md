# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_gml.c

## Purpose

`echoaudio_gml.c` provides common control-register and digital-I/O helpers for Gina24, Mona, and Layla24 class cards. These cards share GML clock, S/PDIF, ADAT, and auto-mute register semantics while differing in ASIC selection and clock-source details.

## Important APIs, Types, and Functions

`check_asic_status()` sends `DSP_VC_TEST_ASIC` and reads the ASIC-loaded response. `write_control_reg()` applies `GML_DIGITAL_IN_AUTO_MUTE`, writes `comm_page->control_register`, clears the handshake, and sends `DSP_VC_WRITE_CONTROL_REG`. `set_input_auto_mute()` updates `chip->digital_in_automute` by reapplying the current input clock. `set_digital_mode()` validates closed pipes and supported mode bits, delegates to card-specific `dsp_set_digital_mode()`, and refreshes monitor/input/output levels when ADAT bus topology changes. `set_professional_spdif()` rebuilds the S/PDIF status bits based on professional/consumer mode and sample rate.

## Control Flow

Card-specific DSP files call `write_control_reg()` for rate, clock, and digital-mode changes. User-facing control changes enter `set_digital_mode()` or `set_input_auto_mute()`, which protect mode changes from active pipes and then republish levels that the DSP may reinterpret when switching ADAT versus S/PDIF routing.

## State and Persistence Behavior

The file persists digital auto-mute, professional S/PDIF, and digital mode in `struct echoaudio` and the comm-page control register. It relies on the card-specific restore path to replay these settings after firmware reload. ADAT transitions may alter logical bus availability, so cached monitor and gain matrices are written back to the DSP.

## Dependencies and Integration Points

It depends on GML constants from `echoaudio_dsp.h`, card-specific `set_input_clock()`, `dsp_set_digital_mode()`, and optional `set_input_gain()`. It is included only by GML card wrappers after their card-specific DSP file and before `echoaudio.c`.

## Risks and Test Signals

Risks include changing digital mode while streams are open, stale auto-mute bits, failing to refresh gains after ADAT changes, and card-specific lock ordering around `write_control_reg()`. Test signals are successful mode switching among S/PDIF RCA/optical and ADAT, expected `-EAGAIN` with open pipes, correct clock controls, and no DSP handshake failures.
