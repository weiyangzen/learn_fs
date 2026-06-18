# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/sun4i-a10.h

Purpose: `sun4i-a10.h` is a Devicetree binding header for a pin controller. It exports numeric C preprocessor
constants that DTS files and provider drivers share as the ABI for phandle cells, selector values,
and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 7 `#define`s covering pinctrl pin, pad, mux, drive,
bias, or electrical configuration cells. The main macro families are SUN4I (7). Representative
constants are `SUN4I_PINCTRL_10_MA`, `SUN4I_PINCTRL_20_MA`, `SUN4I_PINCTRL_30_MA`,
`SUN4I_PINCTRL_40_MA`, `SUN4I_PINCTRL_NO_PULL`, `SUN4I_PINCTRL_PULL_UP`, `SUN4I_PINCTRL_PULL_DOWN`,
`SUN4I_PINCTRL_10_MA`, `SUN4I_PINCTRL_20_MA`, `SUN4I_PINCTRL_30_MA`, `SUN4I_PINCTRL_40_MA`,
`SUN4I_PINCTRL_NO_PULL`, `SUN4I_PINCTRL_PULL_UP`, `SUN4I_PINCTRL_PULL_DOWN`. Function-like helpers
are none. Value shape: literal numeric range 0..3 across 7 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_PINCTRL_SUN4I_A10_H_`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `SUN4I group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 62 lines long. Notable source comments include `Maxime Ripard <maxime.ripard@free-
electrons.com> This file is dual-licensed: you can use it either under the terms of the GPL or the
X11 license, at your option. Note that this dual licensing only applies to this file, and not this
project as a whole. a) This file is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version. This file is distributed in the
hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with this file; if
not, write to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301
USA Or, alternatively, b) Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions: The above copyright notice and
this permission notice shall be included in all copies or substantial portions of the Software. THE
SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.`,
`__DT_BINDINGS_PINCTRL_SUN4I_A10_H_`. Example value clusters are SUN4I: `SUN4I_PINCTRL_10_MA=0`,
`SUN4I_PINCTRL_20_MA=1`, `SUN4I_PINCTRL_30_MA=2`, `SUN4I_PINCTRL_40_MA=3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `SUN4I_PINCTRL_10_MA`, `SUN4I_PINCTRL_20_MA`, `SUN4I_PINCTRL_30_MA`,
`SUN4I_PINCTRL_40_MA`, `SUN4I_PINCTRL_NO_PULL`, `SUN4I_PINCTRL_PULL_UP`, `SUN4I_PINCTRL_PULL_DOWN`.
Test signals include dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe
logs, GPIO loopback, and peripheral bring-up using representative mux groups.
