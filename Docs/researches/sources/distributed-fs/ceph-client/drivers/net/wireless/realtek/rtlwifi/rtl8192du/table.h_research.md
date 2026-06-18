# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/table.h

Purpose: Declares RTL8192DU register-table lengths and exported `u32` table arrays.

Important APIs/data: Defines lengths for PHY, power-group, radio A/B, internal-PA radio A/B, MAC, and AGC tables, and declares matching `extern const u32` arrays.

Control flow/integration: `table.c` defines the arrays. `phy.c` uses the length macros as loop bounds; most tables use pair stride, while the power-group table uses triple stride.

State and persistence: Stateless declarations. The data initializes volatile hardware registers at runtime.

Dependencies: Requires `u32` from Linux types or rtlwifi includes.

Risks/test signals: Length macro drift can truncate programming or overrun arrays. Build tests catch some mismatches; hardware probe and association validate values.
