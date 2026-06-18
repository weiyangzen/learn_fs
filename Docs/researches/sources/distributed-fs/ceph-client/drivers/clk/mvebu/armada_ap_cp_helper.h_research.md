# sources/distributed-fs/ceph-client/drivers/clk/mvebu/armada_ap_cp_helper.h

Purpose: header declaring the AP/CP unique clock-name helper.

Important APIs/types: forward-declares `struct device` and `struct device_node`, and declares `ap_cp_unique_name`.

Control flow: no runtime flow.

State and persistence: no state in the header; the function returns devm-managed names from the C file.

Dependencies and integration: included by AP806/AP807, AP CPU, and CP110 system-controller clock drivers.

Risks: callers must include suitable kernel headers for allocation error handling and must tolerate NULL if the helper is passed NULL.

Test signals: build coverage of all helper users and duplicate-name checks when multiple syscon instances are described in DT.
