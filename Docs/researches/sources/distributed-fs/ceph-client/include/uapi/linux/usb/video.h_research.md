# sources/distributed-fs/ceph-client/include/uapi/linux/usb/video.h

Purpose: Defines USB Video Class constants and descriptor structures for UVC controls, streaming formats, frames, endpoints, color metadata, and payload headers.

Important APIs/types/functions: Constants cover UVC subclasses/protocols, VC/VS/endpoint descriptor subtypes, request codes, terminal/selector/camera/processing/video-stream controls, terminal types, payload flags, and control capabilities. Enums define color primaries, transfer characteristics, and matrix coefficients. Structs model descriptor headers, VC headers, input/output/camera terminals, selector/processing/extension units, control endpoints, input/output streaming headers, color matching, streaming control, uncompressed/MJPEG/frame-based formats and frames, and size macros for variable-length descriptors.

Control flow: Host/gadget code parses descriptors during enumeration, negotiates stream parameters via probe/commit controls, then uses payload header flags (`FID`, `EOF`, `PTS`, `SCR`, etc.) to frame video data over isochronous or bulk endpoints.

State and persistence behavior: Descriptors advertise static capabilities. Runtime state includes selected format/frame interval, camera and processing controls, stream on/off, frame IDs, timestamps, and error flags.

Dependencies and integration points: Includes `linux/types.h`; integrates with UVC kernel driver, V4L2, USB gadget UVC, webcam firmware, and userspace media stacks.

Risks: Variable-length descriptor macros require length validation. Probe/commit values must align with descriptor-supported frames and bandwidth. Payload flags affect frame boundary detection and timestamp sync.

Test signals: Enumerate UVC cameras/gadgets, parse descriptor trees, negotiate multiple formats/frame intervals, stream frames with payload header validation, exercise camera/processing controls, and fuzz malformed descriptors.
