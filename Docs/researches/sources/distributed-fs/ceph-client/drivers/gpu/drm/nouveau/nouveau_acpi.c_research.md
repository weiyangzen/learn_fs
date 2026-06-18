# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_acpi.c

## Purpose

This file handles Nouveau's ACPI integration for hybrid graphics. It detects legacy DSM and Optimus DSM methods, registers a VGA switcheroo handler, programs mux/power DSM calls, prepares Optimus powerdown flags, obtains ACPI panel EDID, and delegates ACPI video backlight registration decisions.

## Important APIs, Types, and Functions

Public functions are `nouveau_is_optimus`, `nouveau_is_v1_dsm`, `nouveau_register_dsm_handler`, `nouveau_unregister_dsm_handler`, `nouveau_switcheroo_optimus_dsm`, `nouveau_acpi_edid`, `nouveau_acpi_video_backlight_use_native`, and `nouveau_acpi_video_register_backlight`. Internal helpers include `nouveau_optimus_dsm`, `nouveau_dsm_get_optimus_functions`, `nouveau_dsm`, `nouveau_dsm_switch_mux`, `nouveau_dsm_set_discrete_state`, `nouveau_dsm_pci_probe`, and `nouveau_dsm_detect`.

## Control Flow

Detection scans display-class PCI devices, checks NVIDIA ACPI handles for the legacy and Optimus DSM GUIDs, records whether mux/power/flags/PR3 support exists, and registers switcheroo when a usable method is found. Switcheroo calls route mux changes to MXM WMI and DSM LED functions and route discrete power changes to DSM power functions. Optimus powerdown first sets flags when supported, then requests PS3 powerdown through the capabilities DSM unless PR3 resources mean DSM should be skipped. EDID access is limited to LVDS/eDP and uses ACPI video.

## State and Persistence Behavior

Static `nouveau_dsm_priv` records DSM/Optimus detection, flags support, PR3 skip behavior, and the ACPI handle. This persists across device registration until module unload; the switcheroo handler is registered only when detection succeeds.

## Dependencies and Integration Points

It depends on ACPI DSM evaluation, PCI topology, MXM WMI, VGA switcheroo, ACPI video EDID/backlight helpers, and DRM connector types. The header provides stubs when ACPI/X86 or switcheroo support is absent.

## Risks

Vendor BIOS DSM behavior is inconsistent; function-0 probing requires a private Optimus DSM implementation. Incorrect PR3/DSM selection can power off hardware incorrectly. PCI scanning heuristics can misclassify integrated/discrete devices. DSM failures are often logged but not fatal.

## Test Signals

Test Optimus and legacy mux laptops, PR3-capable systems, systems without DSM, ACPI EDID on LVDS/eDP, switcheroo on/off and mux switching, suspend/resume power transitions, and builds without ACPI/X86/VGA_SWITCHEROO.
