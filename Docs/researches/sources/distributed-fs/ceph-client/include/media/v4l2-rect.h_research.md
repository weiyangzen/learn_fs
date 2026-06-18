# sources/distributed-fs/ceph-client/include/media/v4l2-rect.h

Purpose: provides inline geometry helpers for `struct v4l2_rect` sizing, containment, equality, intersection, scaling, overlap, and enclosure checks.

Important APIs/types: helpers include `v4l2_rect_set_size_to()`, `v4l2_rect_set_min_size()`, `v4l2_rect_set_max_size()`, `v4l2_rect_map_inside()`, `v4l2_rect_same_size()`, `v4l2_rect_same_position()`, `v4l2_rect_equal()`, `v4l2_rect_intersect()`, `v4l2_rect_scale()`, `v4l2_rect_overlap()`, and `v4l2_rect_enclosed()`.

Control flow: selection/crop/compose code clamps requested rectangles to bounds, compares old/new rectangles, computes intersections for visible regions, scales rectangles between source and destination coordinate spaces, and checks overlap/enclosure before accepting formats or selections.

State and persistence: stateless inline functions mutate only caller-provided rectangle arguments. No allocation or persistent framework state.

Dependencies and integration: includes videodev2 for `struct v4l2_rect`; uses kernel `min/max` helpers. Integrates with selection APIs in ioctl/subdevice paths and any driver crop/compose implementation.

Risks: coordinate addition can overflow for extreme signed values; `v4l2_rect_scale()` rounds horizontal left/width down to even values, which is correct for many video formats but can surprise generic geometry users; zero source width/height clears the rectangle; `v4l2_rect_enclosed()` takes non-const pointers even though it does not mutate them.

Test signals: clamp below min and above max, map rectangles partially and fully outside boundaries, equality and position-only comparisons, non-overlap on touching edges, intersection with empty result, scaling with zero source dimensions, even horizontal rounding, and enclosure at exact boundary edges.
