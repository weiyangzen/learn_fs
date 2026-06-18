# sources/distributed-fs/ceph-client/drivers/comedi/drivers/dac02.c

Purpose: Implements a legacy manually configured Comedi driver for Keithley Metrabyte DAC-02 compatible boards, exposing two 12-bit analog output channels.

Important APIs/types/functions: The range table `das02_ao_ranges` models jumper-selectable voltage/current/external-reference ranges. Register macros `DAC02_AO_LSB()` and `DAC02_AO_MSB()` address each channel's two DAC registers. Main functions are `dac02_attach()` and `dac02_ao_insn_write()`.

Control flow: Attach requests the user-supplied I/O port region in the valid legacy range, allocates one AO subdevice, sets two channels, 12-bit maxdata, range table, write handler, and Comedi readback. AO writes save the unmodified sample in readback, convert bipolar ranges to complementary offset binary by subtracting from maxdata, then write LSB nibble-aligned data followed by MSB to latch the double-buffered DAC.

State and persistence: Runtime state is the I/O base and Comedi AO readback. Physical range selection is controlled by external jumpers and cannot be read by software. DAC output latches persist until overwritten or reset.

Dependencies and integration points: Depends on Comedi legacy attach/detach and I/O-port access. It is manually configured with an I/O port base and has no PCI/PNP discovery, IRQs, calibration, or command path.

Risks: The reported range is user-selected by chanspec but actual electrical range depends on jumpers, so software can request a range that does not match hardware wiring. Bipolar encoding is inverted relative to unipolar and must remain correct. Test signals include valid/invalid I/O base attach, writes to both channels, bipolar/unipolar encoding checks, readback, and latch ordering on real hardware.
