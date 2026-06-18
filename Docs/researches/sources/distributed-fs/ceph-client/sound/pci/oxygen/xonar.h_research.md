
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar.h

Purpose: shared header for Asus Xonar Virtuoso board support and HDMI helpers.

Important types/APIs: `struct xonar_generic` stores anti-pop delay, output-enable GPIO, external power interrupt/register fields, and cached power state. `struct xonar_hdmi` stores five UART command parameters. Prototypes cover output enable/disable, external power monitoring, CS53x1 ADC GPIO setup/rate control, generic GPIO-backed mixer switches, model-provider selectors, and HDMI init/cleanup/resume/PCM params/UART input.

Integration: used by `virtuoso.c`, `xonar_lib.c`, `xonar_cs43xx.c`, `xonar_pcm179x.c`, `xonar_hdmi.c`, and WM87x6 support. It bridges shared Oxygen model callbacks to board-specific model data.

Risks: `xonar_generic` must be first in model-specific structures where helpers cast `chip->model_data`; layout changes can break all helpers. Test signals include output anti-pop sequencing, external power GPIO interrupts, GPIO mixer controls with invert flag, CS53x1 rate changes, and HDMI UART messages.
