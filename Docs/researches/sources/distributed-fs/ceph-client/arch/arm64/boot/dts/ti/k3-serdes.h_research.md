# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/k3-serdes.h

## Purpose
This binding header defines SERDES lane mux constants for TI K3 SoCs.

## APIs, Types, And Constants
The exported constants map SoC, SERDES instance, lane, and function to numeric mux values. Covered families include J721E, J7200, AM64, J721S2, J784S4, and J722S. Functions include PCIe lanes, USB/USB swap, QSGMII/SGMII lanes, eDP lanes, and unused IP slots.

## Control Flow And State
There is no code flow or state. DTS files use these constants in SERDES mux properties; the chosen values become persistent DTB data interpreted by TI SERDES/PHY drivers.

## Dependencies And Integration
The header has no includes. It integrates with K3 board DTS files that route high-speed lanes among PCIe, USB, Ethernet, and display functions.

## Risks And Test Signals
Risks are lane swap mistakes, selecting a mux value not supported by board wiring, or using constants from the wrong SoC family. Test signals include DTB compilation, PHY/PCIe/USB/Ethernet/display probe success, link training, and board-level high-speed interface validation.
