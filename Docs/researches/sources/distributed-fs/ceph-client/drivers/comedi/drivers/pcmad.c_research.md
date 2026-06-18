## sources/distributed-fs/ceph-client/drivers/comedi/drivers/pcmad.c

### Purpose
`pcmad.c` is a simple synchronous analog-input driver for Winsystems PCM-A/D12 and PCM-A/D16 boards, with board-configured single-ended/differential reference and straight-binary or bipolar two's-complement encoding.

### Important APIs, Types, And Functions
`struct pcmad_board_struct` selects 12-bit or 16-bit maximum data. Main functions are `pcmad_ai_eoc()`, `pcmad_ai_insn_read()`, and `pcmad_attach()`.

### Control Flow, State, And Persistence
Attach reserves four I/O ports and creates one AI subdevice. Configuration options select 16 single-ended or 8 differential channels and unipolar 0-5 V or bipolar +/-10 V range. Each read writes the channel number to the convert register, waits until status bits 0 and 1 are both set, reads LSB/MSB, shifts 12-bit board data down by four bits, munges bipolar two's-complement values into Comedi offset-binary form, and returns the requested number of samples. The driver has no persistent runtime state beyond board selection and subdevice configuration.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on Comedi timeout helpers and port I/O. Risks include a likely documentation/option mismatch because comments name option 2/3 while attach checks options 1/2, no IRQ support despite an unused IRQ option in the comments, hardware jumper mismatch not detectable by software, and tight polling-only behavior. Test signals include 12-bit and 16-bit sample formatting, single-ended versus differential channel counts, bipolar munge, timeout on missing EOC bits, and I/O region alignment validation.
