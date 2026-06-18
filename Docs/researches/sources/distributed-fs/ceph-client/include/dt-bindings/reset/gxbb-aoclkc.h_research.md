# sources/distributed-fs/ceph-client/include/dt-bindings/reset/gxbb-aoclkc.h

Purpose: `gxbb-aoclkc.h` is a Devicetree binding header for a reset-controller provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 6 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are RESET_AO (6). Representative constants are
`RESET_AO_REMOTE`, `RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`, `RESET_AO_UART1`, `RESET_AO_UART2`,
`RESET_AO_IR_BLASTER`, `RESET_AO_REMOTE`, `RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`,
`RESET_AO_UART1`, `RESET_AO_UART2`, `RESET_AO_IR_BLASTER`. Function-like helpers are none. Value
shape: literal numeric range 0..5 across 6 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`DT_BINDINGS_RESET_AMLOGIC_MESON_GXBB_AOCLK`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `RESET_AO group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 66 lines long. Notable source comments include `This file is provided under a dual
BSD/GPLv2 license. When using or redistributing this file, you may do so under either license. GPL
LICENSE SUMMARY This program is free software; you can redistribute it and/or modify it under the
terms of version 2 of the GNU General Public License as published by the Free Software Foundation.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details. You should have received a copy of the GNU General Public
License along with this program; if not, see <http://www.gnu.org/licenses/>. The full GNU General
Public License is included in this distribution in the file called COPYING. BSD LICENSE
Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met: * Redistributions of source code must retain the
above copyright notice, this list of conditions and the following disclaimer. * Redistributions in
binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution. * Neither the
name of Intel Corporation nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written permission. THIS SOFTWARE IS
PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.`. Example value clusters are RESET_AO:
`RESET_AO_REMOTE=0`, `RESET_AO_I2C_MASTER=1`, `RESET_AO_I2C_SLAVE=2`, `RESET_AO_UART1=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as `RESET_AO_REMOTE`,
`RESET_AO_I2C_MASTER`, `RESET_AO_I2C_SLAVE`, `RESET_AO_UART1`, `RESET_AO_UART2`,
`RESET_AO_IR_BLASTER`. Test signals include DTS compile checks, reset-controller probe, driver
reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
